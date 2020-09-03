import logging
import os
from logging.handlers import RotatingFileHandler

from telethon import TelegramClient, events
from telethon.sessions import StringSession

from spark import Spark

ENV = bool(os.environ.get('ENV', False))

if ENV:
    from prod_config import Config
else:
    from dev_config import Development as Config

#Log Configuration
if os.path.exists("Spark-Gram.log"):
	with open("Spark-Gram.log", "r+") as f_d:
		f_d.truncate(0)

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%d-%b-%y %H:%M:%S",
    handlers=[
        RotatingFileHandler(
            "Spark-Gram.log",
            maxBytes=Config.LOG_MAX_FILE_SIZE,
            backupCount=10
        ),
        logging.StreamHandler()
    ]
)
logging.getLogger("telethon").setLevel(logging.WARNING)
LOGGER = logging.getLogger(__name__)

if Config.USER_SESSION_STRING is not None:
    # for Running on Heroku
    session_string = str(Config.USER_SESSION_STRING)
    session = StringSession(session_string)
    spark = Spark(
        session,
        config=Config,
        logger=LOGGER
    )
    spark.run_until_disconnected()
else:
    LOGGER.error("USER_SESSION_STRING is mandatory to start session"
                 "\n please Enter USER_SESSION_STRING and restart")
