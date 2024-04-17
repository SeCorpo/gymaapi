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


async def new_gyma_in_db(person_id: int | None, db: AsyncSession = Depends(get_db)) -> Gyma | None:
    if person_id is None:
        raise Exception("Gyma requires a person_id")

    try:
        new_gyma = Gyma(
            person_id=person_id,
            time_of_arrival=datetime.datetime.now()
        )
        db.add(new_gyma)
        await db.commit()
        return new_gyma
    except Exception as e:
        logging.error(e)
        await db.rollback()
        return None


async def set_time_of_departure(person_id: int, gyma_id: int, db: AsyncSession = Depends(get_db)) -> Gyma | None:
    try:
        gyma = await get_gyma_by_gyma_id(gyma_id, db)
        if gyma is None:
            return None

        if gyma.person_id is not person_id:
            raise Exception("Gyma can only be altered by its owner")

        if gyma.time_of_departure is not None:
            return None

        gyma.time_of_departure = datetime.datetime.now()
        await db.commit()
        return gyma

    except Exception as e:
        logging.error(e)
        await db.rollback()
        return None


async def add_exercise_plus_to_gyma(gyma_id: int, person_id: int, exercise_dto: ExerciseDTO,
                                    db: AsyncSession = Depends(get_db)) -> Exercise | None:
    """ Add exercise to db and makes the connection to gyma, so that there won't be loose exercises """
    try:
        gyma = await get_gyma_by_gyma_id(gyma_id, db)
        if gyma is None:
            return None

        if gyma.person_id is not person_id:
            return None

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

        gyma_exercise = GymaExercise(exercise_id=exercise.exercise_id, gyma_id=gyma.gyma_id)
        db.add(gyma_exercise)

        await db.commit()
        return exercise
    except Exception as e:
        logging.error(e)
        await db.rollback()
        return None
