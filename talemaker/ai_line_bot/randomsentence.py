import json
import random

with open('./ai_line_bot/script.json', 'r') as f:
  data = json.load(f)

def pick_a_sentence(situation = 'string', language = 'string'):
    amount = random.randrange(len(data[situation][language]))
    output = data[situation][language][amount]
    return output

if __name__ == '__main__':
    pass