import redis
from .config import settings

def get_redis():
    return redis.Redis(
        host=settings.VALKEY_HOST,
        port=settings.VALKEY_PORT,
        decode_responses=True
    )
