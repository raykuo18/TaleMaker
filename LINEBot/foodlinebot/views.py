from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
 
from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import MessageEvent, TextSendMessage

#圖片引用
from PIL import Image
from datetime import datetime
 
line_bot_api = LineBotApi(settings.LINE_CHANNEL_ACCESS_TOKEN)
parser = WebhookParser(settings.LINE_CHANNEL_SECRET)
 
 
@csrf_exempt
def callback(request):
 
    if request.method == 'POST':
        signature = request.META['HTTP_X_LINE_SIGNATURE']
        body = request.body.decode('utf-8')
 
        try:
            events = parser.parse(body, signature)  # 傳入的事件
        except InvalidSignatureError:
            return HttpResponseForbidden()
        except LineBotApiError:
            return HttpResponseBadRequest()
 
        for event in events:
            print(event)

            if isinstance(event, MessageEvent):  # 如果有訊息事件
                if event.message.type == "image":
                    image_content = line_bot_api.get_message_content(event.message.id) # 傳入的圖片內容
                    print(image_content)
                    
                    image_name = ''.join(str(datetime.now())) # 用傳入圖片的時間取名
                    image_name = image_name.upper()+'.jpg' # 副檔名可以是 .jpg or .png

                    # 把圖檔放到指定的資料夾當中
                    path = './foodlinebot/image/' + image_name
                    with open(path, 'wb') as fd:
                        for chunk in image_content.iter_content():
                            fd.write(chunk)
                    
                    line_bot_api.reply_message( # 回復傳入的訊息文字
                        event.reply_token,
                        TextSendMessage(text="Wait a second, I'm thinking.") # 等待主程式跑的前言
                    )
                    # 主程式放這裡

                else:
                    line_bot_api.reply_message( # 回復傳入的訊息文字
                        event.reply_token,
                        TextSendMessage(text="Please give me a photo.") # 如果user傳文字則要求傳圖片
                    )

        return HttpResponse()
    else:
        return HttpResponseBadRequest()