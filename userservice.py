import config as cfg
from user import User
from usertoken import Token

class UserService():

    def __init__(self):

        #: Init users and admin dict
        self.users = {}
        self.admins = {}
        self.banned = {}
        
        self.tokens = {}

        self.create_new_token(cfg.OWNER_ROLE)


    def create_new_token(self, role: str, valid_for: int = 1):
        token = Token(cfg.ROLE_TO_RANK[role], valid_for)
        self.tokens[token.value] = token

    def remove_token(self, token_id: str):
        pass

    def ban_user(self, id: str):
        if id in self.users:
            user: User = self.users.pop(id)
            self.banned[user.chat_id]

    def unban_user(self, id: str):
        pass

    def activate_token(self, token_id):
        pass