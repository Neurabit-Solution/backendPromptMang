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
        
        # Load file if it exists
        if os.path.exists(config_path):
            with open(config_path, 'rb') as config_file:
                configs.load(config_file)
        
        # Helper to get config from ENV or properties file
        def get_conf(key, default=None):
            env_val = os.environ.get(key.upper())
            if env_val is not None:
                return env_val
            
            prop_val = configs.get(key)
            if prop_val is not None:
                return prop_val.data
            
            return default

        # Database
        self.DB_HOST = get_conf("db_host", "localhost")
        self.DB_PORT = get_conf("db_port", "5432")
        self.DB_NAME = get_conf("db_name", "magicpic")
        self.DB_USER = get_conf("db_user", "admin")
        self.DB_PASSWORD = get_conf("db_password", "admin@123")
        
        self.DATABASE_URL = f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

        # Security
        self.SECRET_KEY = get_conf("secret_key", "your-super-secret-key-change-this-in-production")
        self.ALGORITHM = get_conf("algorithm", "HS256")
        self.ACCESS_TOKEN_EXPIRE_MINUTES = int(get_conf("access_token_expire_minutes", 30))
        self.REFRESH_TOKEN_EXPIRE_DAYS = int(get_conf("refresh_token_expire_days", 7))

settings = Settings()
