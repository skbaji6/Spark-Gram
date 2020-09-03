import importlib.util
import logging
import time
from pathlib import Path

from telethon import TelegramClient
import telethon.utils
import telethon.events


class Spark(TelegramClient):
    def __init__(self, session, *, logger, config):
        self._name = "SparkGram"
        self._logger = logger
        self.config = config
        self._plugins = {}
        self.n_plugin_path = "modules"
        kwargs = {
            "device_model": "BAJI NONUI",
            "app_version": "@Spark 2008.01-SNAPSHOT",
            "lang_code": "en",
            "api_id": config.APP_ID,
            "api_hash": config.API_HASH
        }

        self.sparkbot = None
        if config.BOT_TOKEN is not None:
            self.sparkbot = TelegramClient(
                "SPARK_BOT_SESSION",
                api_id=config.APP_ID,
                api_hash=config.API_HASH
            ).start(bot_token=config.BOT_TOKEN)

        super().__init__(session, **kwargs)
        # self._event_builders = reversed(self._event_builders)
        self.loop.run_until_complete(self._async_init(bot_token=config.BOT_TOKEN))

        core_plugin = Path(__file__).parent / "_core.py"
        self.load_plugin_from_file(core_plugin)
        self.load_plugin("forward")
        self.load_plugin("tmv")

    async def _async_init(self, **kwargs):
        await self.start(**kwargs)

        self.me = await self.get_me()
        self.uid = telethon.utils.get_peer_id(self.me)

        self._logger.info(
            f"Logged in as {self.uid} "
        )

    def load_plugin(self, shortname):
        self.load_plugin_from_file(f"{self.n_plugin_path}/{shortname}.py")

    def load_plugin_from_file(self, path):
        path = Path(path)
        shortname = path.stem
        name = f"_SparkModules.{self._name}.{shortname}"

        spec = importlib.util.spec_from_file_location(name, path)
        mod = importlib.util.module_from_spec(spec)

        mod.spark = self
        mod.logger = logging.getLogger(shortname)
        # declare Config and tgbot to be accessible by all modules
        mod.Config = self.config
        if self.config.BOT_USER_NAME is not None:
            mod.sparkbot = self.sparkbot
        mod.BOT_START_TIME = time.time()

        spec.loader.exec_module(mod)
        self._plugins[shortname] = mod
        self._logger.info(f"Successfully loaded plugin {shortname}")

    def remove_plugin(self, shortname):
        name = self._plugins[shortname].__name__

        for i in reversed(range(len(self._event_builders))):
            ev, cb = self._event_builders[i]
            if cb.__module__ == name:
                del self._event_builders[i]

        del self._plugins[shortname]
        self._logger.info(f"Removed plugin {shortname}")
