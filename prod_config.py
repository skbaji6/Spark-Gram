import os


class Config(object):
    LOG_ENABLE = False
    APP_ID = int(os.environ.get("APP_ID", 6))
    API_HASH = os.environ.get("API_HASH", "bb06d4avfb49gc3eeb1aeb98ae0f571e")
    BOT_TOKEN = os.environ.get("BOT_TOKEN", None)
    BOT_USER_NAME = os.environ.get("BOT_USER_NAME", None)
    USER_SESSION_STRING = os.environ.get("USER_SESSION_STRING", None)
    MONGO_DB_URL = os.environ.get("MONGO_DB_URL", None)
    LOG_MAX_FILE_SIZE = 50000000
    COMMAND_HAND_LER = '\.'
    UB_BLACK_LIST_CHAT = [
        -1001220993104,
        -1001365798550,
        -1001158304289,
        -1001212593743,
        -1001195845680,
        -1001330468518,
        -1001221185967,
        -1001340243678,
        -1001311056733,
        -1001135438308,
        -1001038774929,
        -1001070622614,
        -1001119331451,
        -1001095401841
    ]
    # specify LOAD and NO_LOAD
    LOAD = []
    NO_LOAD = []
