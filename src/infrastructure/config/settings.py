from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://user:password@localhost:5432/saude"
    redis_url: str = "redis://localhost:6379/0"
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"