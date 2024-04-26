from typing import List
from fastapi import APIRouter, Depends, HTTPException
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from dto.exerciseDTO import ExerciseDTO

from dto.gymaDTO import GymaDTO
from service.pubService import get_last_three_gyma_entry

router = APIRouter(prefix="/api/v1/pub", tags=["pub"])


@router.get("/", response_model=List[GymaDTO], status_code=200)
async def get_pub_three_latest(gyma_keys: str = None, db: AsyncSession = Depends(get_db)):
    logging.info(f"Searching for the latest three gyma entries {'excluding: ' + gyma_keys if gyma_keys else ''}")

    pub_three_latest_gyma = await get_last_three_gyma_entry(db, gyma_keys)
    if not pub_three_latest_gyma:
        raise HTTPException(status_code=404, detail="No gyma entries found")

    pub_gyma_with_exercises = []
    for gyma in pub_three_latest_gyma:
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

        pub_gyma_with_exercises.append(gyma_dto)

    return pub_gyma_with_exercises