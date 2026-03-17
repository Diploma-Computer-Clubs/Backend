from redis import asyncio as aioredis
from src.shared.configurations.config import get_redis_url

redis_client = aioredis.from_url(get_redis_url(), decode_responses=True)

async def set_code(phone: str, code: str):
    await redis_client.setex(f"sms:{phone}", 300, code)

async def get_code(phone: str):
    return await redis_client.get(f"sms:{phone}")

async def delete_code(phone: str):
    await redis_client.delete(f"sms:{phone}")