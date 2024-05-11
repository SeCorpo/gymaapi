import logging
import random
import string

from sqlalchemy import select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from model.UserVerification import UserVerification


async def get_user_id_by_verification_code(db: AsyncSession, verification_code: str) -> int | None:
    """ Get user id from verification code. """
    try:
        result = await db.execute(select(UserVerification).filter_by(verification_code=verification_code))
        user_id = result.scalar_one().user_id
        return user_id
    except NoResultFound:
        return None


async def get_verification_code_by_user_id(db: AsyncSession, user_id: int) -> str | None:
    """ Get verification code from user id. """
    try:
        result = await db.execute(select(UserVerification).filter_by(user_id=user_id))
        verification_code = result.scalar_one().verification_code
        return verification_code
    except NoResultFound:
        return None


async def add_user_verification(db: AsyncSession, user_id: int, verification_code: str) -> bool:
    """ Add user_verification to database. Which is made after registering a user to verify its email address. """
    try:
        user_verification = UserVerification(user_id=user_id, verification_code=verification_code)
        db.add(user_verification)
        await db.commit()
        return True
    except Exception as e:
        logging.error(e)
        await db.rollback()
        return False


async def remove_user_verification(db: AsyncSession, user_id: int) -> bool:
    """ Remove user_verification from database. """
    try:
        result = await db.execute(select(UserVerification).filter_by(user_id=user_id))
        user_verification = result.scalars().first()

        if user_verification:
            await db.delete(user_verification)
            await db.commit()
            return True
        else:
            logging.error("No user verification found for user_id: {}".format(user_id))
            return False

    except Exception as e:
        logging.error(e)
        await db.rollback()
        return False


async def generate_verification_code(db: AsyncSession) -> str:
    """ Generates a random alphanumeric string for use as a verification_code and makes sure it's not already used.  """
    letters_and_digits = string.ascii_letters + string.digits
    verification_code = ''.join(random.choice(letters_and_digits) for _ in range(64))

    if await get_user_id_by_verification_code(db, verification_code) is None:
        return verification_code
    else:
        await generate_verification_code(db)
