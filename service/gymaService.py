import logging
from datetime import datetime
from typing import Optional

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from dto.exerciseDTO import ExerciseDTO
from model.Exercise import Exercise
from model.Gyma import Gyma


async def get_gyma_by_gyma_id(gyma_id: int, db: AsyncSession = Depends(get_db)) -> Gyma | None:
    """ Get Gyma object by gyma id from database. """
    try:
        result = await db.execute(select(Gyma).filter_by(gyma_id=gyma_id))
        gyma = result.scalar_one()
        return gyma
    except NoResultFound:
        return None


async def add_gyma(user_id: int | None, db: AsyncSession = Depends(get_db)) -> Gyma | None:
    if user_id is None:
        raise Exception("Gyma requires a person_id")

    try:
        new_gyma = Gyma(
            user_id=user_id,
            time_of_arrival=datetime.now()
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


async def set_time_of_leaving(user_id: int, gyma_id: int, db: AsyncSession = Depends(get_db)) -> Optional[datetime]:
    try:
        gyma = await get_gyma_by_gyma_id(gyma_id, db)
        if gyma is None:
            return None

        if gyma.user_id is not user_id:
            raise Exception("Gyma can only be altered by its owner")

        if gyma.time_of_leaving is not None:
            return None

        gyma.time_of_leaving = datetime.now()
        await db.commit()
        await db.refresh(gyma)
        return gyma.time_of_leaving

    except Exception as e:
        logging.error(e)
        await db.rollback()
        return None
