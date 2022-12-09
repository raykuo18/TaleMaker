from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import MessageEvent, TextSendMessage

from enum import Enum

from utils.utils import str_contain_chinese, chinese_convert, message_obj, pick_a_sentence
from models.models import visual_question_answering, image_captioning

from ai_line_bot.views import ChatBot #i don't even know what i've just import

# Setup LINE Bot api
line_bot_api = LineBotApi(settings.LINE_CHANNEL_ACCESS_TOKEN)
parser = WebhookParser(settings.LINE_CHANNEL_SECRET)

STATES = Enum(
    'states',(
        'IDLE',
        'INIT',
        'SETTING',
        'VQA'
    )
)

class ChatState():
    def __init__(self):
        self.state = STATES.IDLE
        
    def __call__(self):
        return self.state
        
    def change_state(self, state):
        self.state = state
        
        

class UserClass():
    def __init__(self):
        self.users_data = []
        pass
    
    def get_user_data(self, user_id): # TODO: better form
        for user_data in self.users_data:
            if user_data["id"] == user_id:
                return user_data
        print(f"Error: Cannot found user {user_id}!")
        return None
    
    def new_message(self, user_id, message_type):
        if user_id in list([x['id'] for x in self.users_data]):
            user_data = self.get_user_data(user_id)
            if message_type == "sticker" and user_data['state']() != STATES.IDLE:
                user_data['state'].change_state(STATES.IDLE)
                line_bot_api.reply_message(
                    self.reply_token,
                    message_obj(pick_a_sentence("afterleaving", "en"))
                )
            elif user_data['state'] == STATES.IDLE:
                if message_type == "sticker":
                    user_data['state'].change_state(STATES.INIT) 
                    line_bot_api.reply_message(
                        self.reply_token,
                        message_obj(
                            f"Hello {profile.display_name}, welcome to TaleMaker\n"\
                            + f"You can send a image to start the app!"
                        )   #still can't figure it out how to set the profile here
                    )   
                elif message_type != "sticker":
                    line_bot_api.reply_message(
                        self.reply_token,
                        message_obj(pick_a_sentence("greeting", "en"))
                    )

                elif user_data['state'] == STATES.INIT:
                    if message_type == "text":
                        line_bot_api.reply_message(
                            self.reply_token,
                            message_obj(pick_a_sentence("beforeCaptioning", "en"))
                        )
                    elif message_type == "image":
                        user_data['state'].change_state(STATES.VQA)
                        ChatBot.save_and_caption(event=event, userId=user_data["id"])   

                elif user_data['state'] == STATES.VQA:
                    if message_type == "text":
                        ChatBot.answer_the_question(event=event, userId=user_data["id"])
                    elif message_type == "image":
                        ChatBot.save_and_caption(event=event, userId=user_data['id'])
                    #I think it will auto fix when you import back to view.py or use 'img_file' as event    

            else:
                pass
            # TODO: finish the logic

        else: # new user
            new_user_data = {
                "id": user_id,
                "state": ChatState(),
                "img_file": ''
            }
            self.users_data.append(new_user_data)
         