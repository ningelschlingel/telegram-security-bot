from datetime import datetime, timedelta
from dataclasses import dataclass, InitVar, field
from typing import ClassVar
from role import Role
from utils import randomstr
import config as cfg

@dataclass
class Token():
    ''' #TODO
    '''

    #: let class keep track if owner-token was already created
    owner_token_created: ClassVar[bool] = False

    #: init params, value has randomstr as default
    role: Role
    valid_for: InitVar[int]
    value: str = randomstr(cfg.ACTIVATION_TOKEN_LENGTH)

    #: prepare timestamp field 
    valid_until: datetime = field(init=False)
    
    def __post_init__(self, valid_for):
        ''' #TODO
        '''

        #: compute validity timestamp with valid_for value 
        self.valid_until = datetime.today() + timedelta(days=valid_for)

    @classmethod
    def owner_token(cls):
        ''' #TODO
        '''

        if not cls.owner_token_created:
            cls.owner_token_created = True
            return cls(Role.OWNER, 1, cfg.OWNER_ACTIVATION_TOKEN)
    
    def is_valid(self):
        ''' #TODO 
        '''
        
        return datetime.today() < self.valid_until

if __name__ == '__main__':

    t = Token.owner_token()

    print(t)