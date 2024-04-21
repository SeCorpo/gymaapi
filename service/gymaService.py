import logging

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from dto.exerciseDTO import ExerciseDTO
from model.Exercise import Exercise
from model.Gyma import Gyma
import datetime

from model.GymaExercise import GymaExercise


async def get_gyma_by_gyma_id(gyma_id: int, db: AsyncSession = Depends(get_db)) -> Gyma | None:
    """ Get Gyma object by gyma id from database. """
    try:
        result = await db.execute(select(Gyma).filter_by(gyma_id=gyma_id))
        gyma = result.scalar_one()
        return gyma
    except NoResultFound:
        return None


async def new_gyma_in_db(user_id: int | None, db: AsyncSession = Depends(get_db)) -> Gyma | None:
    if user_id is None:
        raise Exception("Gyma requires a person_id")

    try:
        new_gyma = Gyma(
            user_id=user_id,
            time_of_arrival=datetime.datetime.now()
        )
        db.add(new_gyma)
        await db.commit()
        await db.refresh(new_gyma)
        return new_gyma
    except Exception as e:
        logging.error(e)
        logging.info("new_gyma_in_db: Failed to create Gyma")
        await db.rollback()
        return None


async def set_time_of_departure(user_id: int, gyma_id: int, db: AsyncSession = Depends(get_db)) -> Gyma | None:
    try:
        gyma = await get_gyma_by_gyma_id(gyma_id, db)
        if gyma is None:
            return None

        if gyma.user_id is not user_id:
            raise Exception("Gyma can only be altered by its owner")

        if gyma.time_of_departure is not None:
            return None

        gyma.time_of_departure = datetime.datetime.now()
        await db.commit()
        await db.refresh(gyma)
        return gyma

    except Exception as e:
        logging.error(e)
        await db.rollback()
        return None


async def add_exercise(exercise_dto: ExerciseDTO,
                       db: AsyncSession = Depends(get_db)) -> Exercise | None:
    """ Add exercise to db """
    try:
        exercise = Exercise(
            exercise_name=exercise_dto.exercise_name,
            exercise_type=exercise_dto.exercise_type,
            count=exercise_dto.count,
            sets=exercise_dto.sets,
            weight=exercise_dto.weight,
            minutes=exercise_dto.minutes,
            km=exercise_dto.km,
            level=exercise_dto.level,
            description=exercise_dto.description,
            created_at=datetime.datetime.now()
        )

        db.add(exercise)
        await db.commit()
        await db.refresh(exercise)
        return exercise

    except Exception as e:
        logging.error(e)
        await db.rollback()
        return None


async def associate_exercise_with_gyma(exercise: Exercise, gyma_id: int,
                                       db: AsyncSession = Depends(get_db)) -> bool:
    """ Associate exercise with gyma """
    try:
        gyma = await get_gyma_by_gyma_id(gyma_id, db)
        if gyma is None:
            return False

        gyma_exercise = GymaExercise(exercise_id=exercise.exercise_id, gyma_id=gyma.gyma_id)
        db.add(gyma_exercise)

        return True

    except Exception as e:
        logging.error(e)
        await db.rollback()
        return False
