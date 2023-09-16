import os
from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    rabbit_user: str = os.getenv("RABBITMQ_USER", "")
    rabbit_pass: str = os.getenv("RABBITMQ_PASSWORD", "")
    rabbit_host: str = os.getenv("RABBITMQ_HOST", "")

    queue_name: str = os.getenv("QUEUE_NAME", "")
    rpc_queue: str = os.getenv("RPC_QUEUE", "")


@lru_cache()
def get_settings():
    settings = Settings()
    return settings
