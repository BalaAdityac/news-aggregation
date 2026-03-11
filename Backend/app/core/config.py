from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_DB_NAME: str = "news_aggregation"
    NEWSAPI_KEY: Optional[str] = None
    GNEWS_API_KEY: Optional[str] = None
    APP_ENV: str = "development"
    LOG_LEVEL: str = "INFO"
    FEED_REFRESH_INTERVAL_MINUTES: int = 30

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()