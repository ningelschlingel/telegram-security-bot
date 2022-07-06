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
    ''' UserService for basic user management
    '''


    def __init__(self):
        ''' Init

            #: initialising user and token dicts
            #: creates owner token

        '''

        #: Init users, banned and token dict
        self.users: UserDict = UserDict()
        self.banned: UserDict = UserDict()
        self.tokens: Dict[str, Token] = {}

        # Create owner token
        owner_token: Token = Token.owner_token()
        self.tokens[owner_token.value] = owner_token
        self.owner: User = None

    def get_user(self, chat_id: int, default = None) -> Union[User, None]:
        ''' Get user with chat_id, return default if not present
        '''

        return self.users.get(chat_id, default)

    def get_users(self) -> UserDict:
        ''' Get users
        '''
        
        return self.users

    def get_banned(self) -> UserDict:
        ''' Get banned
        '''

        return self.banned

    def get_owner(self) -> Union[User, None]:
        ''' Get owner
        '''

        return self.owner

    def is_owner(self, chat_id) -> bool:
        ''' Check if chat_id belongs to owner

            #: return -> wheter or not the user with given chat_id is the owner
        '''

        return chat_id in self.users and self.owner and self.users[chat_id] == self.owner

    def generate_token(self, role: Role, valid_for: int = 1) -> Token:
        ''' Generates token with given role and validity period in days

            #: return -> generated token
        '''

        token = Token(role, valid_for)
        self.tokens[token.value] = token

        return token

    def remove_user(self, chat_id: int) -> bool:
        ''' Removes user with given chat_id

            #: return -> whether or not the user existed before he eventually was removed
        '''

        if chat_id in self.users:
            del self.users[chat_id]
            return True

        return False

    def remove_token(self, token_id: str) -> bool:
        ''' Removes token with given token_id

            #: return -> whether or not the token existed before it eventually was removed
        '''

        if token_id in self.tokens:

            del self.tokens[token_id]
            return True

        return False

    def clear_tokens(self) -> None:
        ''' Removes all tokens
        '''

        self.tokens.clear()
    
    def remove_expired_tokens(self) -> None:
        ''' Removes all expired tokens 
        '''

        #: Remove expired tokens in dict comprehension filter
        self.tokens = { k:v for k,v in self.tokens.items() if v.is_valid() }

    def activate_token(self, token_id: str, chat_id: int, username: str) -> Union[User, None]:
        ''' Activates token for user with given chat_id and username

            #: Creates user if token is valid
            #: Sets owner if token is owner-token and owner is not yet set

            #: return -> user if activation was successful, else None
        '''

        #: remove expired tokens
        self.remove_expired_tokens()

        #: check if token is valid
        if token_id not in self.tokens:
            return None

        #: invalidate/remove token and create user
        token: Token = self.tokens.pop(token_id)
        user: User = User(chat_id, username, token.role)

        if user.role is Role.OWNER:

            #: No second owner allowed
            if self.owner:
                return None
            
            #: Set owner
            self.owner = user

        #: save to user dict
        self.users[chat_id] = user

        return user

    
    def clear(self) -> None:
        ''' Cleans everything except the owner
        '''

        owner = self.get_owner

        self.tokens.clear()
        
        self.users.clear()
        self.users[owner.chat_id] = owner

    def ban_user(self, chat_id: str) -> bool:
        ''' Moves user from users to banned

            #: return -> whether or not the user was present and moved
        '''

        if chat_id in self.users:
            user: User = self.users.pop(chat_id)
            self.banned[user.chat_id] = user

            return True
        
        return False

    def unban_user(self, chat_id: str) -> bool:
        ''' Moves user from banned to users

            #: return -> whether or not the user was present and moved
        '''

        if chat_id in self.banned:
            user: User = self.banned.pop(chat_id)
            self.users[user.chat_id] = user

            return True
        
        return False

    def get_role_of(self, chat_id: int) -> Union[Role, None]:
        ''' Gets role of user with provided chat_id

            #: return -> role of user if present, else None
        '''

        if chat_id in self.users:
            return self.users[chat_id].role
        return None

    def is_banned(self, chat_id: int) -> bool:
        ''' Gets if user with provided chat_id is banned

            #: User does not necessarly need to be activated

            #: return -> whether or not user with given chat_id is present in banned
        '''

        return chat_id in self.banned

    def user_has_role(self, chat_id: int, role: Role) -> bool:
        ''' Gets if user with provided chat_id has *at least* the provided role

            #: return -> whether or not the user has the role if user is present in users, else None
        '''

        if chat_id in self.users:
            return self.users[chat_id].role >= role
        return None

    def users_as_str(self) -> str:
        ''' Gets all users as string separated by newlines

            #: return -> users as string
        '''

        return self._user_dict_as_str(self.users)

    def banned_as_str(self) -> str:
        ''' Gets all banned users as string separated by newlines

            #: return -> banned as string
        '''

        return self._user_dict_as_str(self.banned)


    def _user_dict_as_str(self, d: UserDict) -> str:
        ''' Helper for stringifying user dicts

            #: return -> user dict as string
        '''

        lst = [str(e) for e in d.values()]
        return '\n'.join(lst)

if __name__=='__main__':

    us = UserService()
    users = us.get_users().with_max_role(Role.MOD).with_max_role(Role.SUB).with_min_role(Role.SUB)

    print(users)

