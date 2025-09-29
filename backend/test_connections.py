#!/usr/bin/env python3
import os
import sys
import psycopg2
import redis
import requests
from time import sleep

def test_postgres():
    try:
        conn = psycopg2.connect(
            host=os.getenv("POSTGRES_HOST", "localhost"),
            port=os.getenv("POSTGRES_PORT", 5432),
            database=os.getenv("POSTGRES_DB", "ai_qa_platform"),
            user=os.getenv("POSTGRES_USER", "admin"),
            password=os.getenv("POSTGRES_PASSWORD", "secure_password_123")
        )
        conn.close()
        print("✅ PostgreSQL connection successful")
        return True
    except Exception as e:
        print(f"❌ PostgreSQL connection failed: {e}")
        return False

def test_redis():
    try:
        r = redis.Redis(
            host=os.getenv("VALKEY_HOST", "localhost"),
            port=os.getenv("VALKEY_PORT", 6379),
            decode_responses=True
        )
        r.ping()
        print("✅ Redis/Valkey connection successful")
        return True
    except Exception as e:
        print(f"❌ Redis/Valkey connection failed: {e}")
        return False

def test_ai_service():
    try:
        response = requests.get(
            f"http://{os.getenv('AI_SERVICE_HOST', 'localhost')}:{os.getenv('AI_SERVICE_PORT', 8001)}/health",
            timeout=5
        )
        if response.status_code == 200:
            print("✅ AI Service connection successful")
            return True
    except Exception as e:
        print(f"❌ AI Service connection failed: {e}")
        return False

if __name__ == "__main__":
    print("Testing connections...")
    postgres_ok = test_postgres()
    redis_ok = test_redis()
    ai_ok = test_ai_service()
    
    if all([postgres_ok, redis_ok, ai_ok]):
        print("\n🎉 All connections successful!")
        sys.exit(0)
    else:
        print("\n⚠️ Some connections failed. Check the logs above.")
        sys.exit(1)
