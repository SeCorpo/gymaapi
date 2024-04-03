import uuid
from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from model.User import User
from database import get_db
from service.userService import get_user_by_email, password_hasher
import bcrypt
from session.sessionDataObject import SessionDataObject
from session.session import set_session, get_session_data, get_person_id_from_session_data


async def login_user(email: str, password: str, db: AsyncSession = Depends(get_db)):
    """ Authenticate user by email and password. """
    user = await get_user_by_email(email, db)

    if user:
        hashing_password = bcrypt.hashpw(password.encode('utf-8'), user.salt)

        if hashing_password == user.password_hash:

            # return init user and gyma data for all pages
            session_data_object = SessionDataObject(
                person_id=user.user_id
            )
            raw_session_key = await set_session(session_data_object)



