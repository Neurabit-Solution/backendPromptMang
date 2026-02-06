import os
from jproperties import Properties

class Settings:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Settings, cls).__new__(cls)
            cls._instance._load_config()
        return cls._instance

    def _load_config(self):
        configs = Properties()
        config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'config.properties')
        
        with open(config_path, 'rb') as config_file:
            configs.load(config_file)
            
        # Database
        self.DB_HOST = configs.get("db_host").data
        self.DB_PORT = configs.get("db_port").data
        self.DB_NAME = configs.get("db_name").data
        self.DB_USER = configs.get("db_user").data
        self.DB_PASSWORD = configs.get("db_password").data
        
        self.DATABASE_URL = f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

        # Security
        self.SECRET_KEY = configs.get("secret_key").data
        self.ALGORITHM = configs.get("algorithm").data
        self.ACCESS_TOKEN_EXPIRE_MINUTES = int(configs.get("access_token_expire_minutes").data)
        self.REFRESH_TOKEN_EXPIRE_DAYS = int(configs.get("refresh_token_expire_days").data)

settings = Settings()
