from dataclasses import dataclass
from typing import Callable

@dataclass
class Payload:

    callback: Callable
    data: object = None
    stage: int = None