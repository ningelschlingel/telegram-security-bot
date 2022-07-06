import enum
import operator

class Role(enum.Enum):

    def __new__(cls, value):
        obj = object.__new__(cls)
        obj._value_ = value
        return obj

    def __init__(self, value):
        self.rank = value

    def __lt__(self, other):
        if self.__class__ is other.__class__:
           return self.value < other.value
        return NotImplemented

    def __ge__(self, other):
        if self.__class__ is other.__class__:
           return self.value >= other.value
        return NotImplemented

    


    OPEN, SUB, MOD, ADMIN, OWNER = range(5)

    min = OPEN
    max = OWNER

if __name__ == '__main__':
    print(Role.min)

    print(operator.ge(Role.ADMIN, Role.MOD))


