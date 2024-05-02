import logging
from datetime import datetime
from typing import Optional

from fastapi import Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from model.Gyma import Gyma


async def get_gyma_by_gyma_id(db: AsyncSession, gyma_id: int) -> Gyma | None:
    """ Get Gyma object by gyma id from database. """
    try:
        result = await db.execute(select(Gyma).filter_by(gyma_id=gyma_id))
        gyma = result.scalar_one()
        return gyma
    except NoResultFound:
        return None


async def add_gyma(db: AsyncSession, user_id: int | None) -> Gyma | None:
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
        return None


async def set_time_of_leaving(db: AsyncSession, user_id: int, gyma: Gyma) -> Optional[datetime]:
    try:
        if gyma is None:
            raise HTTPException(status_code=404, detail="Gyma cannot be found")

        if gyma.user_id is not user_id:
            raise HTTPException(status_code=403, detail="Gyma can only be altered by its owner")

        if gyma.time_of_leaving is not None:
            raise HTTPException(status_code=400, detail="Gyma time_of_leaving has already been set")

        gyma.time_of_leaving = datetime.now()
        await db.commit()
        await db.refresh(gyma)
        return gyma.time_of_leaving

    except Exception as e:
        logging.error(e)
        return None
