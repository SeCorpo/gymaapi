from fastapi import APIRouter, Depends, HTTPException
from database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from dto.personDTO import PersonDTO
from mail.emailService import send_verification_email
from provider.authProvider import check_user_credentials, encode_str, get_auth_key
from dto.loginDTO import LoginDTO, LoginResponseDTO
from service.personService import get_person_by_user_id
from service.userService import get_user_by_email, get_user_by_user_id, set_email_verification
from service.userVerificationService import get_user_id_by_verification_code, remove_user_verification, \
    get_verification_code_by_user_id
from session.sessionService import set_session, delete_session
from session.sessionDataObject import SessionDataObject

router = APIRouter(prefix="/api/v1/auth", tags=["authentication"])


@router.post("/login", response_model=LoginResponseDTO, status_code=200)
async def login(login_dto: LoginDTO, db: AsyncSession = Depends(get_db)):
    logging.info("Attempting login for user with email: " + login_dto.email)

    user = await get_user_by_email(db, login_dto.email)
    if user is None:
        raise HTTPException(status_code=400,
                            detail="User not found")

    user_id_of_ok_credentials = check_user_credentials(user, login_dto.password)
    if user_id_of_ok_credentials is None:
        raise HTTPException(status_code=401,
                            detail="Incorrect email or password")

    if not user.email_verified:
        raise HTTPException(status_code=403,
                            detail="Email not verified. Please check your email to verify your account.")

    session_object_only_user_id = SessionDataObject(user_id=user_id_of_ok_credentials)
    raw_session_key = await set_session(session_object_only_user_id)
    if raw_session_key is None:
        raise HTTPException(status_code=500,
                            detail="Unable to login, please try later")

    person = await get_person_by_user_id(db, user_id_of_ok_credentials)
    encoded_session_key = encode_str(raw_session_key)

    if person is not None:
        person_dto = PersonDTO(
            first_name=person.first_name,
            last_name=person.last_name,
            date_of_birth=person.date_of_birth,
            sex=person.sex,
            city=person.city,
            profile_text=person.profile_text,
        )
    else:
        person_dto = None

    return {
        "session_token": encoded_session_key,
        "personDTO": person_dto
    }


@router.post("/logout", status_code=200)
async def logout(auth_token: str | None = Depends(get_auth_key)):
    logging.info("Attempting logout and session deletion")
    if auth_token is None:
        raise HTTPException(status_code=404, detail="Session does not exist")
    else:
        return await delete_session(auth_token)


@router.get("/verify/{verification_code}", status_code=200)
async def verify(verification_code: str, db: AsyncSession = Depends(get_db)):
    logging.info("Attempting email verification with verification code")
    user_id = await get_user_id_by_verification_code(db, verification_code)
    logging.info(f"Verification code: {verification_code}")
    if user_id is None:
        raise HTTPException(status_code=404, detail="Verification code does not exist")
    else:
        logging.info(f"Verifying user {user_id}")
        user = await get_user_by_user_id(db, user_id)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        else:
            verification_code_removed = await remove_user_verification(db, user_id)
            email_verified = await set_email_verification(db, user)
            if email_verified is True and verification_code_removed is True:
                return True
            else:
                raise HTTPException(status_code=403, detail="Unable to verify email, please contact support")


@router.post("/resend_verification_mail", status_code=200)
async def resend_verification(login_dto: LoginDTO, db: AsyncSession = Depends(get_db)):
    logging.info("Attempting email resend: " + login_dto.email)
    if login_dto.email is None:
        raise HTTPException(status_code=404, detail="Please provide email")
    else:
        user_of_email = await get_user_by_email(db, login_dto.email)
        if user_of_email is None:
            raise HTTPException(status_code=400, detail="User not found")
        elif user_of_email.email_verified:
            raise HTTPException(status_code=403, detail="User already verified")
        else:
            verification_code_from_user_id = await get_verification_code_by_user_id(db, user_of_email.user_id)
            if verification_code_from_user_id is None:
                raise HTTPException(status_code=404, detail="Verification code does not exist, please contact support")
            else:
                email_send = await send_verification_email(verification_code_from_user_id, login_dto.email)
                if email_send:
                    return True
                else:
                    raise HTTPException(status_code=400, detail="Unable to send verification email")
