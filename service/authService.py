import base64
from fastapi import Depends
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


def get_auth_key(headers: dict[str, str]) -> str | None:
    """ Get decoded Authentication token from headers as a string. """
    auth_header = headers.get('Authorization')
    if not auth_header:
        return None

    parts = auth_header.split(' ', maxsplit=1)
    if len(parts) == 2 and parts[0].lower() == 'bearer':
        decoded_session_key = decode_str(parts[1])
        return decoded_session_key
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
