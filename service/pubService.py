import logging
from typing import List
from fastapi import Depends
from sqlalchemy import select, desc
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from model.Gyma import Gyma
from model.GymaExercise import GymaExercise


async def get_last_three_gyma_entry(db: AsyncSession, gyma_keys: str = None) -> List[Gyma] | None:
    """ Get last three gyma entries by time_of_leaving, exclude gyma_keys, for the client already has them. """
    try:
        gyma_keys_to_exclude = [key.strip() for key in (gyma_keys.split(",") if gyma_keys else [])]
        query = (
            select(Gyma)
            .options(joinedload(Gyma.exercises).joinedload(GymaExercise.exercise))
            .order_by(desc(Gyma.time_of_leaving))
            .limit(3)
            .where(Gyma.time_of_leaving.isnot(None))
        )

        if gyma_keys_to_exclude:
            query = query.where(~Gyma.gyma_id.in_(gyma_keys_to_exclude))

        result = await db.execute(query)
        three_latest_gyma = result.scalars().unique().all()

        return list(three_latest_gyma)

    except NoResultFound:
        return None
    except Exception as e:
        logging.error(f"Error fetching gyma entries: {e}")
        return []
