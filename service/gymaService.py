import logging
from datetime import datetime
from typing import Optional

from fastapi import Depends, HTTPException
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


async def add_gyma(user_id: int | None, db: AsyncSession) -> Gyma:
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
        await db.rollback()
        logging.error(f"Failed to create Gyma: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


async def set_time_of_leaving(user_id: int, gyma_id: int, db: AsyncSession = Depends(get_db)) -> Optional[datetime]:
    try:
        gyma = await get_gyma_by_gyma_id(gyma_id, db)
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
        await db.rollback()
        raise HTTPException(status_code=500, detail="Failed to set time of_leave")
