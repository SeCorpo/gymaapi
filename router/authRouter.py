from fastapi import APIRouter, Depends, HTTPException
from database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
import logging
from service.authService import get_user_id_when_login_ok, encode_str
from dto.loginDTO import LoginDTO
from session.session import set_session
from session.sessionDataObject import SessionDataObject

router = APIRouter(prefix="/api/v1/auth", tags=["authentication"])


@router.post("/login", status_code=200)
async def login(login_dto: LoginDTO, db: AsyncSession = Depends(get_db)):
    logging.info("Attempting login for user with email: " + login_dto.email)

    user_id_of_ok_credentials = await get_user_id_when_login_ok(login_dto.email, login_dto.password, db)
    if user_id_of_ok_credentials is None:
        raise HTTPException(status_code=401, detail="Incorrect email or password")

    session_object_only_person_id = SessionDataObject(person_id=user_id_of_ok_credentials)
    raw_session_key = await set_session(session_object_only_person_id)

    if raw_session_key is None:
        raise HTTPException(status_code=500, detail="Unable to login, please try later")

    encoded_session_key = encode_str(raw_session_key)

    return {"session_token": encoded_session_key}

