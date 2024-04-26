from typing import List
from fastapi import APIRouter, Depends
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from dto.exerciseDTO import ExerciseDTO

from dto.gymaDTO import GymaDTO
from service.authService import get_auth_key
from service.mineService import get_last_three_gyma_entry_of_user
from session.sessionService import get_user_id_from_session_data

router = APIRouter(prefix="/api/v1/mine", tags=["mine"])


@router.get("/", status_code=200, response_model=List[GymaDTO])
async def get_mine_three_latest(gyma_keys: str = None,
                                auth_token: str | None = Depends(get_auth_key),
                                db: AsyncSession = Depends(get_db)):
    logging.info(f"Searching for the latest three gyma entries {'excluding: ' + gyma_keys if gyma_keys else ''}")

    user_id: int = await get_user_id_from_session_data(auth_token)
    mine_three_latest_gyma = await get_last_three_gyma_entry_of_user(db, user_id, gyma_keys)

    mine_gyma_with_exercises = []
    for gyma in mine_three_latest_gyma:

        exercise_dtos = [
            ExerciseDTO(
                exercise_name=exercise.exercise.exercise_name,
                exercise_type=exercise.exercise.exercise_type,
                count=exercise.exercise.count,
                sets=exercise.exercise.sets,
                weight=exercise.exercise.weight,
                minutes=exercise.exercise.minutes,
                km=exercise.exercise.km,
                level=exercise.exercise.level,
                description=exercise.exercise.description,
            ) for exercise in gyma.exercises
        ]

        gyma_dto = GymaDTO(
            gyma_id=gyma.gyma_id,
            person=None,  # This should be replaced with a PersonDTO object if required
            time_of_arrival=gyma.time_of_arrival,
            time_of_leaving=gyma.time_of_leaving,
            exercises=exercise_dtos
        )

        mine_gyma_with_exercises.append(gyma_dto)

    return mine_gyma_with_exercises
