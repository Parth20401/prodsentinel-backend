from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "ProdSentinel"
    APP_ENV: str = "local"
    LOG_LEVEL: str = "INFO"
    
    # Database
    DATABASE_URL: str
    
    # Redis (for Celery task queue)
    REDIS_URL: str = "redis://localhost:6379/0"
    
    class Config:
        env_file = ".env"

settings = Settings()
