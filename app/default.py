from enum import Enum

class AccountStatusEnum(Enum):
    INACTIVE = 0
    ACTIVE = 1
    SUSPENDED = 2
    BLOCKED = 3

class YNEnum(Enum):
    NO = 0
    YES = 1
