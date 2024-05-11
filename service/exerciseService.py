import logging
from datetime import datetime
from typing import List

from fastapi import Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from dto.exerciseDTO import ExerciseDTO
from model.Exercise import Exercise
from model.GymaExercise import GymaExercise


async def get_exercise_by_exercise_id(db: AsyncSession, exercise_id: int) -> Exercise | None:
    """ Get Exercise object by exercise id from database. """
    try:
        result = await db.execute(select(Exercise).filter_by(exercise_id=exercise_id))
        exercise = result.scalar_one()
        return exercise
    except NoResultFound:
        return None


async def get_exercises_by_gyma_id(db: AsyncSession, gyma_id: int) -> List[Exercise] | None:
    """ Get list of Exercise objects by gyma id from database. """
    try:
        result = await db.execute(select(Exercise).filter_by(gyma_id=gyma_id))
        exercises = result.scalars().all()
        return list(exercises)
    except NoResultFound:
        return None


async def add_exercise_db(db: AsyncSession, gyma_id: int, exercise_dto: ExerciseDTO) -> bool:
    """ Add a new exercise to a Gyma and create a record in GymaExercise table. """
    try:
        new_exercise = Exercise(
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
        db.add(new_exercise)
        await db.commit()
        await db.refresh(new_exercise)

        gyma_exercise = GymaExercise(gyma_id=gyma_id, exercise_id=new_exercise.exercise_id)
        db.add(gyma_exercise)
        await db.commit()

        if gyma_exercise and new_exercise is not None:
            return True
        HTTPException(status_code=500, detail="Failed to add new exercise and connection to gyma.")
    except Exception as e:
        logging.error(f"Error adding exercise to gyma: {e}")
        await db.rollback()
        return False
