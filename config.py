from distutils.command.config import config
from pydantic import BaseSettings

import nonebot

global_config = nonebot.get_driver().config.dict()

class Config(BaseSettings):
    # Your Config Here
    superusers = global_config.get("superusers") if global_config.get("superusers") else ["924579723"]
    class Config:
        extra = "ignore"