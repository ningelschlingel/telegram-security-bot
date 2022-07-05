from dataclasses import dataclass

from usertoken import Token

@dataclass
class User():
    chat_id: str
    name: str
    role: int
    #activation_token: str