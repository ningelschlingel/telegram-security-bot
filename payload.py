from dataclasses import dataclass
from typing import Callable

@dataclass
class Payload:

    data: object
    stage: int
    callback: Callable