from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    database_url: str
    secret_key: str
    sendgrid_api_key: Optional[str] = None
    log_level: str = "INFO"
    encryption_key_id: str = "v1"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()

