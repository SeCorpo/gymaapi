from fastapi import APIRouter, Depends, HTTPException, Body
import logging

from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from dto.exerciseDTO import ExerciseDTO
from dto.gymaDTO import GymaDTO
from service.authService import get_auth_key
from service.exerciseService import add_exercise
from session.sessionService import get_user_id_from_session_data, set_gyma_id_in_session, get_session_data, \
    delete_gyma_id_from_session
from service.gymaService import add_gyma, set_time_of_leaving

router = APIRouter(prefix="/api/v1/gyma", tags=["gyma"])


@router.post("/start", response_model=GymaDTO, status_code=201)
async def start_gyma(auth_token: str | None = Depends(get_auth_key),
                     db: AsyncSession = Depends(get_db)):

    if auth_token is None:
        raise HTTPException(status_code=404, detail="Session does not exist")

    user_id = await get_user_id_from_session_data(auth_token)
    gyma = await add_gyma(user_id, db)

    logging.info(f"New gyma_id: {gyma.gyma_id}")

    if await set_gyma_id_in_session(auth_token, gyma.gyma_id):
        return gyma

    return HTTPException(status_code=404, detail="Gyma cannot be set in session")


@router.put("/end")
async def end_gyma(auth_token: str | None = Depends(get_auth_key),
                   db: AsyncSession = Depends(get_db)):
    if auth_token is None:
        raise HTTPException(status_code=404, detail="Session does not exist")

    session_data = await get_session_data(auth_token)

    if session_data.gyma_id is None:
        raise HTTPException(status_code=404, detail="Gyma does not exist in session")

    time_of_leaving = await set_time_of_leaving(session_data.user_id, session_data.gyma_id, db)

    if await delete_gyma_id_from_session(auth_token):
        return {"time_of_leaving": time_of_leaving}

    return HTTPException(status_code=404, detail="Gyma cannot be removed from session")


@router.post("/exercise", response_model=ExerciseDTO, status_code=201)
async def add_exercise_to_gyma(exercise_dto: ExerciseDTO = Body(...),
                               auth_token: str | None = Depends(get_auth_key),
                               db: AsyncSession = Depends(get_db)):

    if auth_token is None:
        raise HTTPException(status_code=400, detail="Session does not exist")

    session_data = await get_session_data(auth_token)
    if session_data.gyma_id is None:
        raise HTTPException(status_code=400, detail="Gyma does not exist in session")

    exercise = await add_exercise(session_data.gyma_id, exercise_dto, db)
    if exercise is None:
        raise HTTPException(status_code=400, detail="Exercise cannot be added")

    return exercise
