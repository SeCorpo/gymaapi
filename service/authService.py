import base64
import logging

from fastapi import Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from service.userService import get_user_by_email
import bcrypt


async def get_user_id_when_login_ok(email: str, password: str, db: AsyncSession = Depends(get_db)) -> int | None:
    """ Checking email and password credentials against database. Returns user obj or None. """
    user = await get_user_by_email(email, db)

    if user is not None:
        hashing_password = bcrypt.hashpw(password.encode('utf-8'), user.salt)

        if hashing_password == user.password_hash:
            return user.user_id

        else:
            return None
    else:
        return None


def get_auth_key(authorization: str = Header(default=None)) -> str | None:
    """ Get decoded Authentication token from headers as a string. """
    if authorization:
        logging.info(authorization)
        decoded_key = decode_str(authorization)
        logging.info(decoded_key)
        return decoded_key
    else:
        return None


def encode_str(text: str) -> str:
    """ Encode a string using base64. Used for sending encoded session_token to client. """
    encoded_bytes = base64.b64encode(text.encode('utf-8'))
    encoded_str = encoded_bytes.decode('utf-8')
    return encoded_str


def decode_str(encoded_str: str) -> str:
    """Decode a base64 encoded string."""
    decoded_bytes = base64.b64decode(encoded_str.encode('utf-8'))
    decoded_str = decoded_bytes.decode('utf-8')
    return decoded_str
