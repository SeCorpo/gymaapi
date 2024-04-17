from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.exc import NoResultFound

from database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
import bcrypt
import logging
from model.User import User


async def register_user(email: str, password: str, db: AsyncSession = Depends(get_db)) -> bool:
    """ Registers a new user to database. """
    try:
        salt, hashed_password = password_hasher(password)

        user = User(
            email=email,
            salt=salt,
            password_hash=hashed_password,
        )
        db.add(user)
        await db.commit()
        return True

    except Exception as e:
        logging.error(e)
        await db.rollback()
        return False


async def get_user_by_user_id(user_id: int, db: AsyncSession = Depends(get_db)) -> User | None:
    """ Get User object by user id from database. """
    try:
        result = await db.execute(select(User).filter_by(user_id=user_id))
        user = result.scalar_one()
        return user
    except NoResultFound:
        return None


async def get_user_by_email(email: str, db: AsyncSession = Depends(get_db)) -> User | None:
    """ Get User object by email from database. """
    try:
        result = await db.execute(select(User).filter_by(email=email))
        user = result.scalar_one()
        return user
    except NoResultFound:
        return None


async def email_available(email: str, db: AsyncSession = Depends(get_db)) -> bool:
    """ Check if email is already registered. """
    result = await db.execute(select(User).filter_by(email=email))
    user_exists = result.scalar()
    return user_exists is None


def password_hasher(password_plain: str) -> (bytes, bytes):
    """ Hashes a password using bcrypt and generates a random salt. """
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password_plain.encode('utf-8'), salt)

    return salt, hashed_password
