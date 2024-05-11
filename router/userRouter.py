from fastapi import APIRouter, Depends, HTTPException
from database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from mail.emailService import send_verification_email
from service.userService import add_user, email_available
from dto.registerDTO import RegisterDTO
from service.userVerificationService import add_user_verification, generate_verification_code

router = APIRouter(prefix="/api/v1/user", tags=["user"])


@router.post("/", status_code=201)
async def register(register_dto: RegisterDTO, db: AsyncSession = Depends(get_db)):
    logging.info("Trying to registering user with email: " + register_dto.email)

    if not await email_available(db, register_dto.email):
        raise HTTPException(status_code=400, detail="Email is not available")

    user = await add_user(db, register_dto.email, register_dto.password)
    if user is None:
        raise HTTPException(status_code=400, detail="Unable to create user")
    else:
        verification_code = await generate_verification_code(db)
        user_verification_added = await add_user_verification(db, user.user_id, verification_code)
        if not user_verification_added:
            raise HTTPException(status_code=400, detail="Unable to create user_verification")
        else:
            email_send = await send_verification_email(verification_code, "s1koldewijn@gmail.com")
            if email_send:
                return True
            else:
                raise HTTPException(status_code=400, detail="Unable to send verification email")
