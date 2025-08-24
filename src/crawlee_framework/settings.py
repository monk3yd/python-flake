from typing import Dict
# from utils.csv import read_csv
# from loguru import logger

class Settings:
    def __init__(self, spider: Dict[str, str]) -> None:
        self.SPIDER_ID = spider["id"]
        self.SPIDER_NAME = spider["name"]

# NOTE: Change accordingly when starting a new project
spider_settings = {"id": "00", "name": "example"}
settings = Settings(spider_settings)
