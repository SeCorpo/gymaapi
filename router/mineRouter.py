from typing import List
from fastapi import APIRouter, Depends
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from dto.exerciseDTO import ExerciseDTO

from dto.gymaDTO import GymaDTO
from service.authService import get_auth_key
from service.exerciseService import get_exercises_by_gyma_id
from service.mineService import get_last_three_gyma_entry_of_user
from session.sessionService import get_user_id_from_session_data

router = APIRouter(prefix="/api/v1/mine", tags=["mine"])


@router.get("/", status_code=200, response_model=List[GymaDTO])
async def get_mine_three_latest(gyma_keys: str = None,
                                # auth_token: str | None = Depends(get_auth_key),
                                db: AsyncSession = Depends(get_db)):
    logging.info(f"Searching for the latest three gyma entries {'excluding: ' + gyma_keys if gyma_keys else ''}")

    # user_id: int = await get_user_id_from_session_data(auth_token)
    user_id = 1
    three_latest_gyma = await get_last_three_gyma_entry_of_user(user_id, gyma_keys, db)

    gyma_with_exercises = []
    for gyma in three_latest_gyma:
        exercises_of_gyma = await get_exercises_by_gyma_id(gyma.gyma_id, db)

        exercise_dtos = []
        for exercise in exercises_of_gyma:
            exercise_dto = ExerciseDTO(
                exercise_name=exercise.exercise_name,
                exercise_type=exercise.exercise_type,
                count=exercise.count,
                sets=exercise.sets,
                weight=exercise.weight,
                minutes=exercise.minutes,
                km=exercise.km,
                level=exercise.level,
                description=exercise.description,
            )
            exercise_dtos.append(exercise_dto)

        gyma_dto = GymaDTO(
            gyma_id=gyma.gyma_id,
            time_of_arrival=gyma.time_of_arrival,
            time_of_leaving=gyma.time_of_leaving,
            exercises=exercise_dtos,
        )

        gyma_with_exercises.append(gyma_dto)

    return gyma_with_exercises
