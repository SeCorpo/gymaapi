from fastapi import APIRouter, Depends, HTTPException
import logging

from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from dto.exerciseDTO import ExerciseDTO
from dto.gymaDTO import GymaDTO
from service.authService import get_auth_key
from session.sessionService import get_user_id_from_session_data, set_gyma_id_in_session, get_session_data
from service.gymaService import new_gyma_in_db, set_time_of_departure, add_exercise_plus_to_gyma

router = APIRouter(prefix="/api/v1/gyma", tags=["gyma"])


@router.post("/start", response_model=GymaDTO)
async def start_gyma(auth_token: str | None = Depends(get_auth_key),
                     db: AsyncSession = Depends(get_db)):

    if auth_token is None:
        raise HTTPException(status_code=404, detail="Session does not exist")

    user_id = await get_user_id_from_session_data(auth_token)
    gyma = await new_gyma_in_db(user_id, db)

    logging.info(f"New gyma_id: {gyma.gyma_id}")

    if await set_gyma_id_in_session(auth_token, gyma.gyma_id):
        return gyma

    return HTTPException(status_code=404, detail="Gyma cannot be set in session")


@router.put("/end", response_model=GymaDTO)
async def end_gyma(auth_token: str | None = Depends(get_auth_key),
                   db: AsyncSession = Depends(get_db)):
    if auth_token is None:
        raise HTTPException(status_code=404, detail="Session does not exist")

    session_data = await get_session_data(auth_token)

    if session_data.gyma_id is None:
        raise HTTPException(status_code=404, detail="Gyma does not exist in session")

    gyma = await set_time_of_departure(session_data.user_id, session_data.gyma_id, db)

    if await set_gyma_id_in_session(auth_token, None):
        return gyma

    return HTTPException(status_code=404, detail="Gyma cannot be removed from session")








