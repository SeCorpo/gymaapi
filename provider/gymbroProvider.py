import logging
from typing import List
from sqlalchemy import select, desc, or_
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from model.Friendship import Friendship

from model.Gyma import Gyma
from model.GymaExercise import GymaExercise


async def get_last_ten_gyma_entries_of_user_and_friends(db: AsyncSession,
                                                        user_id: int, gyma_keys: str = None) -> List[Gyma] | None:
    """ Get last ten gyma entries of user and user's friends by time_of_leaving,
    include associated exercises. """

    try:
        gyma_keys_to_exclude = gyma_keys.split(",") if gyma_keys else []

        friends_query = (
            select(Friendship.friend_id)
            .where(Friendship.person_id == user_id)
        )

        friends_result = await db.execute(friends_query)
        friend_ids = [row[0] for row in friends_result.fetchall()]

        if not friend_ids:
            return []

        query = (
            select(Gyma)
            .options(joinedload(Gyma.exercises).joinedload(GymaExercise.exercise))
            .where(
                or_(
                    Gyma.user_id == user_id,
                    Gyma.user_id.in_(friend_ids)
                )
            )
            .where(~Gyma.gyma_id.in_(gyma_keys_to_exclude))
            .where(Gyma.time_of_leaving.isnot(None))
            .order_by(desc(Gyma.time_of_leaving))
            .limit(10)
        )

        result = await db.execute(query)
        ten_latest_gyma = result.scalars().unique().all()

        return list(ten_latest_gyma)

    except NoResultFound:
        return None
    except Exception as e:
        logging.error(f"Error fetching gyma entries: {e}")
        return []
