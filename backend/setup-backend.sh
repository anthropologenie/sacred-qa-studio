#!/bin/bash

echo "🚀 Setting up Sacred QA Studio Backend Structure..."

# Create all directories first
echo "📁 Creating directory structure..."
mkdir -p backend/app/{core,api/v1/{endpoints,dependencies},models,schemas,crud,services}
mkdir -p backend/tests/{unit,integration}
mkdir -p backend/scripts

# Create __init__.py files
echo "📝 Creating __init__.py files..."
touch backend/app/__init__.py
touch backend/app/core/__init__.py
touch backend/app/api/__init__.py
touch backend/app/api/v1/__init__.py
touch backend/app/models/__init__.py
touch backend/app/schemas/__init__.py
touch backend/app/crud/__init__.py
touch backend/app/services/__init__.py

# Create core configuration files
echo "⚙️ Creating configuration files..."
cat > backend/app/core/config.py << 'EOF'
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
EOF

cat > backend/app/core/database.py << 'EOF'
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
EOF

cat > backend/app/core/redis.py << 'EOF'
import redis
from .config import settings

def get_redis():
    return redis.Redis(
        host=settings.VALKEY_HOST,
        port=settings.VALKEY_PORT,
        decode_responses=True
    )
EOF

# Create main.py
echo "🎯 Creating main application file..."
cat > backend/app/main.py << 'EOF'
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Sacred QA Studio", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"app": "Sacred QA Studio", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "backend"}

@app.get("/api/v1/test")
async def test_endpoint():
    return {"message": "API v1 test endpoint working"}
EOF

# Update requirements.txt with pydantic-settings
echo "📦 Updating requirements.txt..."
if ! grep -q "pydantic-settings" backend/requirements.txt; then
    echo "pydantic-settings==2.3.4" >> backend/requirements.txt
fi

echo "✅ Backend structure created successfully!"
echo ""
echo "📂 Created structure:"
tree -L 3 backend/app/ 2>/dev/null || ls -la backend/app/

echo ""
echo "🎉 Setup complete! Now you can run:"
echo "  docker-compose build"
echo "  docker-compose up -d"
