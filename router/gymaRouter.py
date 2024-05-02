from fastapi import APIRouter, Depends, HTTPException, Body
import logging

from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from dto.exerciseDTO import ExerciseDTO
from dto.gymaDTO import GymaDTO
from service.authService import get_auth_key
from service.exerciseService import add_exercise_db
from session.sessionDataObject import SessionDataObject
from session.sessionService import get_user_id_from_session_data, set_gyma_id_in_session, get_session_data, \
    delete_gyma_id_from_session
from service.gymaService import add_gyma, set_time_of_leaving, get_gyma_by_gyma_id

router = APIRouter(prefix="/api/v1/gyma", tags=["gyma"])


@router.post("/start", response_model=GymaDTO, status_code=201)
async def start_gyma(auth_token: str | None = Depends(get_auth_key),
                     db: AsyncSession = Depends(get_db)):

    user_id = await get_user_id_from_session_data(auth_token)
    if user_id is None:
        raise HTTPException(status_code=401, detail="Session invalid")
    else:
        gyma = await add_gyma(db, user_id)
        if gyma is None:
            raise HTTPException(status_code=404, detail="Gyma cannot be added")
        else:
            if await set_gyma_id_in_session(auth_token, gyma.gyma_id):
                return gyma
            else:
                return HTTPException(status_code=404, detail="Gyma cannot be set in session")


@router.put("/end")
async def end_gyma(auth_token: str | None = Depends(get_auth_key),
                   db: AsyncSession = Depends(get_db)):

    session_data = await get_session_data(auth_token)
    if session_data or session_data.gyma_id or session_data.user_id is None:
        raise HTTPException(status_code=404, detail="Session invalid")
    else:
        gyma = await get_gyma_by_gyma_id(db, session_data.gyma_id)
        if gyma is None:
            raise HTTPException(status_code=404, detail="Gyma does not exist in database")
        else:
            time_of_leaving = await set_time_of_leaving(db, session_data.user_id, gyma)
            if time_of_leaving is None:
                raise HTTPException(status_code=500, detail="Failed to set time of_leave")
            else:
                if await delete_gyma_id_from_session(auth_token):
                    return {"time_of_leaving": time_of_leaving}
                else:
                    return HTTPException(status_code=500, detail="Gyma cannot be removed from session")


@router.post("/exercise", status_code=201)
async def add_exercise_to_gyma(exercise_dto: ExerciseDTO = Body(...),
                               session: SessionDataObject = Depends(get_session_data),
                               db: AsyncSession = Depends(get_db)):

    if session or session.gyma_id is None:
        raise HTTPException(status_code=404, detail="Session invalid")
    else:
        added_exercise = await add_exercise_db(db, session.gyma_id, exercise_dto)
        if added_exercise:
            return added_exercise
        else:
            raise HTTPException(status_code=400, detail="Failed to add exercise")
