from config import Config
from models.database import Database


class BaseService:
    def __init__(self, config: Config, database: Database):
        self._config = config
        self._database = database
