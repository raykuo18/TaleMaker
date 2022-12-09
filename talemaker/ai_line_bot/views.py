from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
 
from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import MessageEvent, TextSendMessage

import os
from enum import Enum
from PIL import Image
from datetime import datetime

from utils.utils import str_contain_chinese, chinese_convert, message_obj, pick_a_sentence
from models.models import visual_question_answering, image_captioning


 
# Setup LINE Bot api
line_bot_api = LineBotApi(settings.LINE_CHANNEL_ACCESS_TOKEN)
parser = WebhookParser(settings.LINE_CHANNEL_SECRET)

class ChatBot():
  def __init__(self):
    print("A new ChatBot is created!!!")
    ChatBot.states = Enum(
      'states',(
        'IDLE',
        'INIT',
        'SETTING',
        'VQA'
      )
    )
    ChatBot.bot_state = ChatBot.states.IDLE
    ChatBot.image_file = ''
  
  def reset(self):
    ChatBot.image_file = ''
    
  @classmethod
  def save_and_caption(cls, event, userId):
    image_content = line_bot_api.get_message_content(event.message.id) # 傳入的圖片內容
    time = datetime.now().strftime("%m%d-%H%M%S-") # 用傳入圖片的時間取名
    ChatBot.image_file = os.path.join(os.getcwd(), "images", time + event.message.id + '.jpg')
    with open(ChatBot.image_file, 'wb') as fd:
      for chunk in image_content.iter_content():
        fd.write(chunk)
    line_bot_api.reply_message( # 回復傳入的訊息文字
      event.reply_token,
      message_obj(pick_a_sentence("afterCaptioning", "en"))
    )
    # TODO: Download the model
    caption = image_captioning(ChatBot.image_file)['caption'] # type: ignore
    # caption = "[Caption msg]"
    line_bot_api.push_message(
      userId,
      message_obj([f"{caption}", pick_a_sentence("afterdescription", "en")])
    )
    
  @classmethod
  def answer_the_question(cls, event, userId):
    line_bot_api.reply_message(
      event.reply_token,
      message_obj(f"Thinking ...")
    )
    answer = visual_question_answering(ChatBot.image_file, event.message.text)['text'] # type: ignore
    line_bot_api.push_message(
      userId,
      message_obj([f"{answer}", pick_a_sentence("aftereveryoutput", "en")])
    )

  @classmethod
  @csrf_exempt
  def callback(cls, request):
    if request.method == 'POST':
      signature = request.META['HTTP_X_LINE_SIGNATURE']
      body = request.body.decode('utf-8')

      try:
        events = parser.parse(body, signature)  # 傳入的事件
      except InvalidSignatureError:
        return HttpResponseForbidden()
      except LineBotApiError:
        return HttpResponseBadRequest()

      for event in events: # type: ignore
        if isinstance(event, MessageEvent):
          # Get some information
          message_type = event.message.type
          # Weired bug!
          userId = event.source.user_id
          profile = line_bot_api.get_profile(userId) # display_name / user_id / picture_url / status_message
          
          
          if message_type == "sticker" and ChatBot.bot_state != ChatBot.states.IDLE: # Reset
            ChatBot.bot_state = ChatBot.states.IDLE # State change
            line_bot_api.reply_message(
              event.reply_token,
              message_obj(pick_a_sentence("afterleaving", "en"))
            )
            
              
          elif ChatBot.bot_state == ChatBot.states.IDLE:
            if message_type == "sticker": # Start
              ChatBot.bot_state = ChatBot.states.INIT # state change
              line_bot_api.reply_message(
                event.reply_token,
                message_obj(
                  f"Hello {profile.display_name}, welcome to TaleMaker\n"\
                  + f"You can send a image to start the app!"
                #   + f"\nType the following command if you want to change the default settings:\n"\
                #   + f"[TODO],\n"\
                #   + f"[TODO],\n"\
                #   + f"[TODO]"
              
                )
              )
            elif message_type != "sticker":
              line_bot_api.reply_message(
                event.reply_token,
                message_obj(pick_a_sentence("greeting", "en"))
              )
              
          elif ChatBot.bot_state == ChatBot.states.INIT:
            if message_type == "text":
              # TODO: parse and setting
              line_bot_api.reply_message(
                event.reply_token,
                message_obj(pick_a_sentence("beforeCaptioning", "en"))
              )
            elif message_type == "image":
              ChatBot.bot_state = ChatBot.states.VQA # State change
              ChatBot.save_and_caption(event=event, userId=userId)
              
          elif ChatBot.bot_state == ChatBot.states.VQA:
            if message_type == "text":
              ChatBot.answer_the_question(event=event, userId=userId)
            elif message_type == "image":
              ChatBot.save_and_caption(event=event, userId=userId)
          
          else:
            pass

      return HttpResponse()
    else:
      return HttpResponseBadRequest()
    
ChatBot()

if __name__ == "__main__":
  pass