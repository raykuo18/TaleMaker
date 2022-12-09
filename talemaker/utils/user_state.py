from enum import Enum

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
                
            # TODO: finish the logic
        else: # new user
            new_user_data = {
                "id": user_id,
                "state": ChatState(),
                "img_file": ''
            }
            self.users_data.append(new_user_data)
         