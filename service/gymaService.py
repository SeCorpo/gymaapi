import logging

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from model.Gyma import Gyma
import datetime


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
        return None
