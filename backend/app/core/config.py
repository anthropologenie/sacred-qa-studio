from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "Sacred QA Studio"
    VERSION: str = "0.1.0"
    DEBUG: bool = False
    
    POSTGRES_HOST: str = "postgres"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "admin"
    POSTGRES_PASSWORD: str = "secure_password_123"
    POSTGRES_DB: str = "ai_qa_platform"
    
    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    
    VALKEY_HOST: str = "valkey"
    VALKEY_PORT: int = 6379
    
    AI_SERVICE_HOST: str = "ai-inference"
    AI_SERVICE_PORT: int = 8001
    
    class Config:
        env_file = ".env"

settings = Settings()
