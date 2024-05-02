import base64
import logging

from fastapi import Header, HTTPException
from model.User import User
import bcrypt


def check_user_credentials(user: User, password: str) -> int | None:
    """ Checking email and password credentials against database. Returns user obj or None. """

    if user or password is None:
        return None
    else:
        hashing_password = bcrypt.hashpw(password.encode('utf-8'), user.salt)
        if hashing_password == user.password_hash:
            return user.user_id
        else:
            return None


def get_auth_key(authorization: str = Header(default=None)) -> str:
    """ Get decoded Authentication token from headers as a string. """
    if not authorization:
        raise HTTPException(status_code=401, detail="Authentication credentials were not provided.")

    try:
        logging.info(f"Authorization header received: {authorization}")
        decoded_key = decode_str(authorization)
        logging.info(f"Decoded key: {decoded_key}")
        return decoded_key
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials.")


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
