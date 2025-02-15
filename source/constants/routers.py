from enum import StrEnum


class RouterInfo(StrEnum):
    prefix = "/api"
    auth_tags = "auth"
    user_tags = "user"
    admin_tags = "admin"

class Endpoints(StrEnum):
    SIGNUP = "/signup"
    TOKEN = "/auth"
    INFO = "/info"
    SEND_COINS = "/sendCoin"
    BUY = "/buy/{item}"

    ADD_USER = "/addUser"
    ADD_MERCH = "/addMerch"
    DELETE_USER = "/deleteUser"
    UPDATE_USER = "/updateUser"
