from fastapi import APIRouter, Depends, HTTPException
from database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
import logging
from service.authService import login_user
from dto.loginDTO import LoginDTO

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/login")
async def login(login_dto: LoginDTO, db: AsyncSession = Depends(get_db)):
    logging.info("Attempting login for user with email: " + login_dto.email)

    user = await login_user(login_dto.email, login_dto.password, db)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect email or password")

    return {"message": "Login successful", "user_id": user.id}
