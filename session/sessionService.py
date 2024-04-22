import logging
import string
import random
import aioredis
import pydantic
import os

from aioredis import RedisError
from dotenv import load_dotenv
from session.sessionDataObject import SessionDataObject

load_dotenv()

expire_time = int(os.getenv("SESSION_EXPIRE_TIME_SECONDS"))
_redis_connection = None  # Cached Redis connection object


async def create_redis_connection():
    """ Create and return an asynchronous Redis connection object. """
    global _redis_connection
    if _redis_connection is None:
        redis_host = os.getenv("REDIS_HOST")
        redis_port = int(os.getenv("REDIS_PORT"))
        redis_db = int(os.getenv("REDIS_DB"))

        try:
            _redis_connection = await aioredis.from_url(
                f"redis://{redis_host}:{redis_port}/{redis_db}", decode_responses=True
            )
        except RedisError as e:
            logging.error(f"Error connecting to Redis: {e}")
            return None

    return _redis_connection


async def get_session_data(key: str) -> SessionDataObject | None:
    """ Retrieve the session data as a SessionDataObject from Redis. """
    try:
        redis_connection = await create_redis_connection()
    except RedisError as e:
        logging.error(e)
        return None

    session_data = await redis_connection.hgetall(key)
    if session_data:
        try:
            await redis_connection.expire(key, expire_time)

            return SessionDataObject(**session_data)
        except pydantic.ValidationError as e:
            logging.error(f"Invalid session data format: {e}")
            return None
    else:
        return None


async def get_user_id_from_session_data(key: str) -> int | None:
    try:
        session_data_object: SessionDataObject = await get_session_data(key)
        return session_data_object.user_id
    except pydantic.ValidationError as e:
        logging.error(f"Invalid session data format: {e}")
        return None


async def get_gyma_id_from_session_data(key: str) -> int | None:
    try:
        session_data_object: SessionDataObject = await get_session_data(key)
        gyma_id = session_data_object.gyma_id
        if gyma_id is None:
            return None
        return gyma_id
    except pydantic.ValidationError as e:
        logging.error(f"Invalid session data format: {e}")
        return None


async def set_session(session_data: SessionDataObject, key: str | None = None) -> str | None:
    """ Stores session data in Redis with a randomly generated key and expiration time. """
    try:
        redis_connection = await create_redis_connection()
        if redis_connection is None:
            logging.error(f"Redis connection failed")
            return None

        if key is None:
            key = await generate_random_key()

        data_dict = {k: v for k, v in session_data.dict().items() if v is not None}
        async with redis_connection:
            await redis_connection.hmset(key, data_dict)
            await redis_connection.expire(key, expire_time)

        return key
    except RedisError as e:
        logging.error(f"Error setting session data in Redis: {e}")
        return None


async def set_gyma_id_in_session(key: str, gyma_id: int) -> bool:
    """ Adds gyma_id to the existing session data. """
    session_data: SessionDataObject = await get_session_data(key)
    if session_data is None:
        return False

    session_data.gyma_id = gyma_id
    raw_session_token = await set_session(session_data, key)
    if raw_session_token is not None:
        return True

    logging.error("Unable to set gyma_id to session data")
    return False


async def delete_gyma_id_from_session(key: str) -> bool:
    """ Deletes gyma_id from the existing session data. """
    if key is None:
        return False
    session_data: SessionDataObject = await get_session_data(key)
    if session_data.gyma_id is None:
        return False
    try:
        redis_connection = await create_redis_connection()
        if redis_connection is None:
            logging.error(f"Redis connection failed")
            return False
        await redis_connection.hdel(key, "gyma_id")
        await redis_connection.expire(key, expire_time)
    except RedisError as e:
        logging.error(f"Error deleting gyma_id from session data: {e}")
        return False


async def delete_session(key: str) -> bool:
    """ Deletes the session data from Redis. """
    try:
        redis_connection = await create_redis_connection()
        if redis_connection is None:
            logging.error(f"Redis connection failed")
            return False

        if key and await get_session_data(key) is not None:
            async with redis_connection:
                await redis_connection.delete(key)
                logging.info(f"Deleted session data from Redis: {key}")
                return True

    except RedisError as e:
        logging.error(f"Error deleting session data in Redis (key: {key}): {e}")
        return False


async def generate_random_key(length: int = 16) -> str:
    """Generates a random alphanumeric string for use as a session key and makes sure it's not already used. """
    logging.info("Generating random key for session key")
    letters_and_digits = string.ascii_letters + string.digits
    key = ''.join(random.choice(letters_and_digits) for _ in range(length))

    if await get_session_data(key) is None:
        return key
    else:
        await generate_random_key()
