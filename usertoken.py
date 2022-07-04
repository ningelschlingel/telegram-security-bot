from datetime import datetime, timedelta
from dataclasses import dataclass, InitVar, field
from utils import randomstr
import config as cfg

@dataclass
class Token():

    role: int
    valid_for: InitVar[int]
    valid_until: datetime = field(init=False)
    value: str = field(init=False)
    
    
    def __post_init__(self, valid_for):
        self.value = randomstr(cfg.TOKEN_LENGTH)
        self.valid_until = datetime.today() + timedelta(days=valid_for)
    
    def is_valid(self):
        return datetime.today() < self.valid_until
