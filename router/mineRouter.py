from typing import List
from fastapi import APIRouter, Depends
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db

from dto.gymaDTO import GymaDTO
from service.authService import get_auth_key
from service.mineService import get_last_three_gyma_entry_of_user
from session.sessionService import get_user_id_from_session_data

router = APIRouter(prefix="/api/v1/mine", tags=["mine"])


@router.get("/", status_code=200)
async def get_mine_three_latest(gyma_keys: str = None,
                                auth_token: str | None = Depends(get_auth_key),
                                db: AsyncSession = Depends(get_db)):
    logging.info(f"Searching for the latest three gyma entries {'excluding: ' + gyma_keys if gyma_keys else ''}")

    user_id: int = await get_user_id_from_session_data(auth_token)
    gyma_with_exercises = await get_last_three_gyma_entry_of_user(user_id, gyma_keys, db)

    return gyma_with_exercises
