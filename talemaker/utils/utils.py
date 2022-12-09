import os
from opencc import OpenCC
from linebot.models import TextSendMessage
import json
import random

def str_contain_chinese(str: str):
  for x in str:
    if u'\u4e00' <= x <= u'\u9fa5':
      return True
  return False

def chinese_convert(str: str, mode='s2twp'):
  # ref: https://reurl.cc/kqyNYL
  cc = OpenCC('mode')
  return cc.convert(str)

def message_obj(message):
  if type(message) is list:
    return [TextSendMessage(text=x) for x in message]
  else:
    return TextSendMessage(text=message)
  
def pick_a_sentence(situation = 'string', language = 'string'):
    with open(os.path.join(os.getcwd(), 'utils/script.json'), 'r') as f:
        data = json.load(f)
    amount = random.randrange(len(data[situation][language]))
    output = data[situation][language][amount]
    return output
  
if __name__ == '__main__':
  pass