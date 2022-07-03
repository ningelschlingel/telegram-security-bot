from dataclasses import dataclass

@dataclass
class User():
    chat_id: str
    name: str
    role: int