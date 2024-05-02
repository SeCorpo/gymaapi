from fastapi import APIRouter, Depends, HTTPException
from database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
import logging
from service.authService import check_user_credentials, encode_str, get_auth_key
from dto.loginDTO import LoginDTO
from service.userService import get_user_by_email
from session.sessionService import set_session, delete_session
from session.sessionDataObject import SessionDataObject

router = APIRouter(prefix="/api/v1/auth", tags=["authentication"])


@router.post("/login", status_code=200)
async def login(login_dto: LoginDTO, db: AsyncSession = Depends(get_db)):
    logging.info("Attempting login for user with email: " + login_dto.email)

    user = await get_user_by_email(db, login_dto.email)
    if user is None:
        raise HTTPException(status_code=400, detail="User not found")
    else:
        user_id_of_ok_credentials = check_user_credentials(user, login_dto.password)
        if user_id_of_ok_credentials is None:
            raise HTTPException(status_code=401, detail="Incorrect email or password")
        else:
            session_object_only_user_id = SessionDataObject(user_id=user_id_of_ok_credentials)
            raw_session_key = await set_session(session_object_only_user_id)
            if raw_session_key is None:
                raise HTTPException(status_code=500, detail="Unable to login, please try later")
            else:
                encoded_session_key = encode_str(raw_session_key)
                return {"session_token": encoded_session_key}


@router.post("/logout", status_code=200)
async def logout(auth_token: str | None = Depends(get_auth_key)):
    logging.info("Attempting logout and session deletion")
    if auth_token is None:
        raise HTTPException(status_code=404, detail="Session does not exist")
    else:
        return await delete_session(auth_token)

