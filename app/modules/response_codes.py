from enum import Enum


class ResponseCodes(Enum):
    OK = 0
    ACCESS_DENIED = 1
    ALREADY_ACTIVE = 2
    INACTIVE = 3
    UNKNOWN_COMMAND = 4
