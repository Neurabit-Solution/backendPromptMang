import configparser
import os
from typing import List
from pydantic_settings import BaseSettings

# Load configuration from config.properties outside the Pydantic model
_config = configparser.ConfigParser()
_config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "config.properties")
_config.read(_config_path)

class Settings(BaseSettings):
    PROJECT_NAME: str = "MagicPic Admin API"
    API_V1_STR: str = "/api/admin"
    
    # Database - initialized from config.properties
    DB_HOST: str = _config.get("database", "db_host", fallback="localhost")
    DB_PORT: str = _config.get("database", "db_port", fallback="5432")
    DB_USER: str = _config.get("database", "db_user", fallback="myuser")
    DB_PASSWORD: str = _config.get("database", "db_password", fallback="example")
    DB_NAME: str = _config.get("database", "db_name", fallback="magicpic")

    # Security - initialized from config.properties
    SECRET_KEY: str = _config.get("security", "secret_key", fallback="YOUR_SUPER_SECRET_KEY_CHANGE_THIS")
    ALGORITHM: str = _config.get("security", "algorithm", fallback="HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(_config.get("security", "access_token_expire_minutes", fallback="30"))

    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8080",
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ]

settings = Settings()
