from dataclasses import dataclass
from role import Role

@dataclass
class User():
    chat_id: int
    name: str
    role: Role = Role.OPEN

    def __repr__(self):
        return '{:14} [ {:6s} ]'.format(self.name, self.role.name.lower())

if __name__=='__main__':

    u = User(123, 'username', Role.ADMIN)

    print(u)

    print(36**8)