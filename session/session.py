import logging
from datetime import datetime, timedelta
import string
import random
import aioredis
import pydantic
import os
from dotenv import load_dotenv

from sessionDataObject import SessionDataObject

load_dotenv()

expire_time = int(os.getenv("SESSION_EXPIRE_TIME_SECONDS"))
_redis_connection = None  # Cached Redis connection object


async def create_redis_connection():
    """ Create and return an asynchronous Redis connection object. """
    global _redis_connection
    if _redis_connection is None:
        redis_host = os.getenv("REDIS_HOST", "localhost")
        redis_port = int(os.getenv("REDIS_PORT", "6379"))
        redis_db = int(os.getenv("REDIS_DB", "0"))

        _redis_connection = await aioredis.from_url(
            f"redis://{redis_host}:{redis_port}/{redis_db}", decode_responses=True
        )
    return _redis_connection


async def get_session_data(key) -> SessionDataObject | None:
    """ Retrieve the session data as a SessionDataObject from Redis. """
    redis_connection = await create_redis_connection()
    session_data = await redis_connection.hgetall(key)
    if session_data:
        try:
            await redis_connection.expire(key, expire_time)

            decoded_data = {k: v.decode() for k, v in session_data.items()}
            return SessionDataObject(**decoded_data)
        except pydantic.ValidationError as e:
            logging.error(f"Invalid session data format: {e}")
            return None
    else:
        return None


async def get_person_id_from_session_data(key) -> int:
    try:
        session_data_object = await get_session_data(key)
        return session_data_object.person_id
    except pydantic.ValidationError as e:
        logging.error(f"Invalid session data format: {e}")


async def get_gyma_id_from_session_data(key) -> int:
    try:
        session_data_object = await get_session_data(key)
        return session_data_object.gyma_id
    except pydantic.ValidationError as e:
        logging.error(f"Invalid session data format: {e}")


async def set_session(session_data: SessionDataObject) -> str:
    """ Stores session data in Redis with a randomly generated key and expiration time. """
    redis_connection = await create_redis_connection()
    key = generate_random_key()
    encoded_data = {k: v.encode() for k, v in session_data.dict().items()}
    await redis_connection.hsetall(key, encoded_data)
    await redis_connection.expire(key, expire_time)
    return key


def generate_random_key(length: int = 16) -> str:
    """Generates a random alphanumeric string for use as a session key. """
    letters_and_digits = string.ascii_letters + string.digits
    return ''.join(random.choice(letters_and_digits) for _ in range(length))
