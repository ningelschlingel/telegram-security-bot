from dataclasses import dataclass

from usertoken import Token

@dataclass
class User():
    id: str
    name: str
    role: int
    #activation_token: str