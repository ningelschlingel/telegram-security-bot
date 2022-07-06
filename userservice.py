import string
import operator
from typing import Dict, Type, TypeVar, Union

import utils
from role import Role
from user import User
from usertoken import Token

T = TypeVar('T', bound='UserDict')

class UserDict(dict):

    def __setitem__(self, key: int, value: User):
        super(UserDict, self).__setitem__(key, value)

    @classmethod
    def from_dict(cls: Type[T], d: dict) -> T:
        userdict = cls()
        userdict.update(d)

        return userdict

    def _filter(self, operator: operator, role: Role) -> T:
        return self.from_dict(dict(filter(lambda kv: operator(kv[1].role, role), self.items())))

    def with_min_role(self, role: Role) -> T: return self._filter(operator.ge, role)
    def with_max_role(self, role: Role) -> T: return self._filter(operator.le, role)
    def with_lower_role(self, role: Role) -> T: return self._filter(operator.lt, role)
    def with_higher_role(self, role: Role) -> T: return self._filter(operator.gt, role)


class UserService():
    ''' #TODO
    '''


    def __init__(self):
        ''' #TODO
        '''

        #: Init users, banned and token dict
        self.users: UserDict[int, User] = UserDict()
        self.banned: UserDict[int, User] = UserDict()
        self.tokens: Dict[str, Token] = {}

        # Create owner token
        owner_token: Token = Token.owner_token()
        self.tokens[owner_token.value] = owner_token
        self.owner: User = None

        #TODO remove test users
        
        for i in range(4):
            user = User(int(utils.randomstr(10, string.digits)), utils.randomstr(8, string.ascii_lowercase), Role(i))
            self.users[user.chat_id] = user

    def get_users(self) -> UserDict:
        ''' #TODO
        '''
        
        return self.users

    def get_banned(self) -> UserDict:
        '''
        '''

        return self.banned

    def get_owner(self) -> Union[User, None]:
        '''
        '''

        return self.owner

    def is_owner(self, chat_id) -> bool:
        '''
        '''

        return chat_id in self.users and self.owner and self.users[chat_id] == self.owner

    def generate_token(self, role: Role, valid_for: int = 1) -> Token:
        ''' #TODO
        '''

        token = Token(role, valid_for)
        self.tokens[token.value] = token

        return token

    def remove_user(self, chat_id: int) -> bool:
        '''
        '''

        if chat_id in self.users:
            del self.users[chat_id]
            return True

        return False

    def remove_token(self, token_id: str) -> bool:
        ''' #TODO
        '''

        if token_id in self.tokens:

            del self.tokens[token_id]
            return True

        return False

    def clear_tokens(self):
        '''
        '''

        self.tokens.clear()
    
    def remove_expired_tokens(self) -> None:
        ''' #TODO   
        '''

        #: Remove expired tokens in dict comprehension filter
        self.tokens = { k:v for k,v in self.tokens.items() if v.is_valid() }

    def activate_token(self, token_id, chat_id, username) -> Union[Role, None]:
        ''' #TODO
        '''

        self.remove_expired_tokens()

        #: 
        if token_id not in self.tokens:
            return None

        #: invalidate/remove token and create user
        token: Token = self.tokens.pop(token_id)
        user = User(chat_id, username, token.role)

        if user.role is Role.OWNER:

            #: No second owner allowed
            if self.owner:
                return None
            
            #: Set owner
            self.owner = user

        #: save to user dict
        self.users[chat_id] = user

        return user

    
    def clear(self):
        '''
        '''

        owner = self.get_owner
        
        self._send_text_msg_to_lst(self.users, 'Your subscription was terminated.')

        self.tokens.clear()
        
        self.users.clear()
        self.users[owner.chat_id] = owner

    def ban_user(self, id: str) -> bool:
        ''' #TODO
        '''

        if id in self.users:
            user: User = self.users.pop(id)
            self.banned[user.chat_id] = user

            return True
        
        return False

    def unban_user(self, id: str) -> bool:
        ''' #TODO
        '''

        if id in self.banned:
            user: User = self.banned.pop(id)
            self.users[user.chat_id] = user

            return True
        
        return False

    def get_role_of(self, chat_id: int) -> Union[Role, None]:
        ''' #TODO
        '''

        if chat_id in self.users:
            return self.users[chat_id].role
        return None

    def is_banned(self, chat_id: int) -> bool:
        ''' #TODO
        '''

        return chat_id in self.banned

    def user_has_role(self, chat_id: int, role: Role) -> bool:
        ''' #TODO
        '''

        if chat_id in self.users:
            return self.users[chat_id].role >= role
        return None

    def users_as_str(self) -> str:
        '''
        '''

        return self._user_dict_as_str(self.users)

    def banned_as_str(self) -> str:
        '''
        '''
        return self._user_dict_as_str(self.banned)


    def _user_dict_as_str(self, d: UserDict[int, User]) -> str:
        '''
        '''

        lst = [str(e) for e in d.values()]
        return '\n'.join(lst)

if __name__=='__main__':

    us = UserService()
    users = us.get_users().with_max_role(Role.MOD).with_max_role(Role.SUB).with_min_role(Role.SUB)

    print(users)

