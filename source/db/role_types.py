from enum import StrEnum, auto


class RoleType(StrEnum):
    user = auto()
    admin = auto()
    deleted = auto()

if __name__ == '__main__':
    print(RoleType.user)
