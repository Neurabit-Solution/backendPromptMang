import os
from jproperties import Properties
from urllib.parse import quote_plus

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
        
        # Helper to get config from ENV or properties file (strip to avoid malformed AWS auth)
        def get_conf(key, default=None):
            env_val = os.environ.get(key.upper())
            if env_val is not None:
                return env_val.strip() if isinstance(env_val, str) else env_val
            
            prop_val = configs.get(key)
            if prop_val is not None and prop_val.data is not None:
                return prop_val.data.strip() if isinstance(prop_val.data, str) else prop_val.data
            
            return default

        # Database
        self.DB_HOST = get_conf("db_host", "localhost")
        self.DB_PORT = get_conf("db_port", "5432")
        self.DB_NAME = get_conf("db_name", "magicpin")
        self.DB_USER = get_conf("db_user", "admin")
        self.DB_PASSWORD = get_conf("db_password", "admin@123")
        
        # URL encode password to handle special characters like '@'
        encoded_password = quote_plus(self.DB_PASSWORD)
        self.DATABASE_URL = f"postgresql://{self.DB_USER}:{encoded_password}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

        # Security
        self.SECRET_KEY = get_conf("secret_key", "your-super-secret-key-change-this-in-production")
        self.ALGORITHM = get_conf("algorithm", "HS256")
        self.ACCESS_TOKEN_EXPIRE_MINUTES = int(get_conf("access_token_expire_minutes", 30))
        self.REFRESH_TOKEN_EXPIRE_DAYS = int(get_conf("refresh_token_expire_days", 7))

        # AWS S3
        self.AWS_ACCESS_KEY_ID     = get_conf("aws_access_key_id", "")
        self.AWS_SECRET_ACCESS_KEY = get_conf("aws_secret_access_key", "")
        self.AWS_REGION            = get_conf("aws_region", "ap-south-1")
        self.AWS_S3_BUCKET         = get_conf("aws_s3_bucket", "magicpic-bucket")

        # Gemini AI
        self.GEMINI_API_KEY = get_conf("gemini_api_key", "")

        # Firebase
        self.FIREBASE_PROJECT_ID = get_conf("firebase_project_id", "")
        # One of: B64 (for .env/deploy), raw JSON string, or file path
        self.FIREBASE_SERVICE_ACCOUNT_B64 = get_conf("firebase_service_account_b64", "")
        self.FIREBASE_SERVICE_ACCOUNT_JSON = get_conf("firebase_service_account_json", "")
        self.FIREBASE_SERVICE_ACCOUNT_PATH = get_conf("firebase_service_account_path", "")

settings = Settings()
