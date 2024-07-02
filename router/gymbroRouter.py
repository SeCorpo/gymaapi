import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from dto.exerciseDTO import ExerciseDTO
from dto.gymaDTO import GymaDTO
from dto.personDTO import PersonSimpleDTO
from provider.authProvider import get_auth_key
from provider.gymbroProvider import get_last_ten_gyma_entries_of_user_and_friends
from service.personService import get_person_by_user_id
from session.sessionService import get_user_id_from_session_data

router = APIRouter(prefix="/api/v1/gymbro", tags=["gymbro"])


@router.get("/", response_model=List[GymaDTO], status_code=200)
async def get_gymbro_ten_latest(gyma_keys: str = None,
                                auth_token: str | None = Depends(get_auth_key),
                                db: AsyncSession = Depends(get_db)):
    logging.info(f"Searching for the latest ten gyma entries {'excluding: ' + gyma_keys if gyma_keys else ''}")

    user_id = await get_user_id_from_session_data(auth_token)
    if user_id is None:
        raise HTTPException(status_code=401, detail="Session invalid")
    else:
        gymbro_ten_latest_gyma = await get_last_ten_gyma_entries_of_user_and_friends(db, user_id, gyma_keys)

        gymbro_gyma_with_exercises = []
        for gyma in gymbro_ten_latest_gyma:
            person_of_gyma = await get_person_by_user_id(db, gyma.user_id)

            person_simple_dto = PersonSimpleDTO(
                profile_url=person_of_gyma.profile_url,
                first_name=person_of_gyma.first_name,
                last_name=person_of_gyma.last_name,
                sex=person_of_gyma.sex,
                pf_path_m=person_of_gyma.pf_path_m,
            )

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
                person=person_simple_dto,
                time_of_arrival=gyma.time_of_arrival,
                time_of_leaving=gyma.time_of_leaving,
                exercises=exercise_dtos
            )

            gymbro_gyma_with_exercises.append(gyma_dto)

        return gymbro_gyma_with_exercises
