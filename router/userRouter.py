from fastapi import APIRouter, Depends, HTTPException
from database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
import logging
from service.userService import register_user, email_available
from dto.registerDTO import RegisterDTO

router = APIRouter(prefix="/user", tags=["user"])


@router.post("/", status_code=201)
async def register(register_dto: RegisterDTO, db: AsyncSession = Depends(get_db)):
    logging.info("Registering user with email: " + register_dto.email)

    if not await email_available(register_dto.email, db):
        raise HTTPException(status_code=400, detail="Email is not available")

    return await register_user(register_dto.email, register_dto.password, db)


