import os

from redis.asyncio import ConnectionError, Redis

redis: "Redis[str]" = Redis.from_url(
    os.environ.get("REDIS_URL", "redis://localhost:6379"),
    decode_responses=True,  # redis.get()이 byte 대신 str을 리턴
    socket_timeout=5,
    retry_on_timeout=True,  # 타임 아웃 발생 시 재시도
    retry_on_error=[ConnectionError],  # 커넥션 에러가 발생 했을 때 재시도
)
