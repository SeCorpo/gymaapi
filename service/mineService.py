from typing import List
from fastapi import Depends
from sqlalchemy import select, desc
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db

from model.Gyma import Gyma


async def get_last_three_gyma_entry_of_user(user_id: int, gyma_keys: str = None,
                                            db: AsyncSession = Depends(get_db)) -> List[Gyma] | None:
    """ Get last three gyma entries of person by time_of_leaving,
    exclude gyma_keys, for the client already has them. """

    try:
        query = (
            select(Gyma)
            .order_by(desc(Gyma.time_of_leaving))
            .limit(3)
            .where(user_id is user_id)
            .where(Gyma.gyma_id.notin_(gyma_keys.split(",") if gyma_keys else []))
            .where(Gyma.time_of_leaving.isnot(None))
        )

        result = await db.execute(query)
        three_latest_gyma = result.scalars().all()

        return list(three_latest_gyma)

    except NoResultFound:
        return None
