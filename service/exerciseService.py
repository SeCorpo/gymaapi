import logging
from datetime import datetime
from typing import List

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from dto.exerciseDTO import ExerciseDTO
from model.Exercise import Exercise
from service.gymaService import get_gyma_by_gyma_id


async def get_exercise_by_exercise_id(exercise_id: int, db: AsyncSession = Depends(get_db)) -> Exercise | None:
    """ Get Exercise object by exercise id from database. """
    try:
        result = await db.execute(select(Exercise).filter_by(exercise_id=exercise_id))
        exercise = result.scalar_one()
        return exercise
    except NoResultFound:
        return None


async def get_exercises_by_gyma_id(gyma_id: int, db: AsyncSession = Depends(get_db)) -> List[Exercise] | None:
    """ Get list of Exercise objects by gyma id from database. """
    try:
        result = await db.execute(select(Exercise).filter_by(gyma_id=gyma_id))
        exercises = result.scalars().all()
        return list(exercises)
    except NoResultFound:
        return None


async def add_exercise(gyma_id: int, exercise_dto: ExerciseDTO,
                       db: AsyncSession = Depends(get_db)) -> Exercise | None:
    """ Add exercise to db """
    gyma = await get_gyma_by_gyma_id(gyma_id, db)
    if gyma is None:
        return None

    try:
        exercise = Exercise(
            gyma_id=gyma_id,
            exercise_name=exercise_dto.exercise_name,
            exercise_type=exercise_dto.exercise_type,
            count=exercise_dto.count,
            sets=exercise_dto.sets,
            weight=exercise_dto.weight,
            minutes=exercise_dto.minutes,
            km=exercise_dto.km,
            level=exercise_dto.level,
            description=exercise_dto.description,
            created_at=datetime.now()
        )

        db.add(exercise)
        await db.commit()
        await db.refresh(exercise)

        return exercise

    except Exception as e:
        logging.error(e)
        await db.rollback()
        return None
