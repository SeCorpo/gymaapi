import logging
from datetime import date

from sqlalchemy import select, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from model.Friendship import Friendship
from model.Person import Person


async def get_friends_by_person_id(db: AsyncSession, person_id: int) -> list[Person]:
    """ Get all accepted friends for a given person by their person_id. """
    result = await db.execute(
        select(Person).join(Person.friends).where(
            and_(
                or_(
                    and_(Friendship.person_id == person_id, Friendship.status == "accepted"),
                    and_(Friendship.friend_id == person_id, Friendship.status == "accepted")
                ),
                Person.person_id != person_id
            )
        ).options(joinedload(Person.friends)).distinct()
    )
    return list(result.scalars().unique().all())


async def get_friendship(db: AsyncSession, person_id: int, friend_id: int) -> Friendship | None:
    """ Get friendship connection. """
    try:
        logging.info(f"Getting friendship for {person_id} and {friend_id}")
        result = await db.execute(
            select(Friendship).where(
                or_(
                    and_(Friendship.person_id == person_id, Friendship.friend_id == friend_id),
                    and_(Friendship.person_id == friend_id, Friendship.friend_id == person_id)
                )
            )
        )
        friendship = result.scalar_one_or_none()
        return friendship
    except Exception as e:
        logging.error(f"Failed to get friendship: {e}")
        return None


async def get_friendship_of_requester(db: AsyncSession, person_id: int, friend_id: int) -> Friendship | None:
    """ Get friendship object; person_id is the requesting party, friend_id is the receiving party. """
    try:
        result = await db.execute(
            select(Friendship).where(
                and_(Friendship.person_id == person_id, Friendship.friend_id == friend_id)
            )
        )
        friendship = result.scalar_one_or_none()
        return friendship
    except Exception as e:
        logging.error(f"Failed to get friendship of requester: {e}")
        return None


async def add_friendship(db: AsyncSession, person_id: int, friend_id: int) -> bool:
    """ Add a new friendship. """
    try:
        new_friendship = Friendship(
            person_id=person_id,
            friend_id=friend_id,
            status='pending',
            since=date.today()
        )
        db.add(new_friendship)
        await db.commit()
        await db.refresh(new_friendship)
        return True
    except Exception as e:
        await db.rollback()
        logging.error(f"Failed to add friendship: {e}")
        return False


async def update_friendship_status(db: AsyncSession, friendship: Friendship, status: str) -> bool:
    """ Update the status of a friendship. """
    try:
        friendship.status = status
        await db.commit()
        return True
    except Exception as e:
        await db.rollback()
        logging.error(f"Failed to update friendship status: {e}")
        return False


async def remove_friendship(db: AsyncSession, friendship: Friendship) -> bool:
    """ Remove a friendship. """
    try:
        await db.delete(friendship)
        await db.commit()
        return True
    except Exception as e:
        await db.rollback()
        logging.error(f"Failed to remove friendship: {e}")
        return False


async def get_pending_friendships_to_be_accepted(db: AsyncSession, person_id: int) -> list[Person]:
    """ Get all persons who have sent pending friendship requests to the given person. """
    result = await db.execute(
        select(Person).join(Friendship, Friendship.person_id == Person.person_id).where(
            and_(
                Friendship.friend_id == person_id,
                Friendship.status == 'pending'
            )
        ).options(joinedload(Person.friends)).distinct()
    )
    return list(result.scalars().unique().all())


async def get_blocked_friendships(db: AsyncSession, person_id: int) -> list[Person]:
    """ Get all persons blocked by person_id. """
    result = await db.execute(
        select(Person).join(Friendship).where(
            and_(
                Friendship.person_id == person_id,
                Friendship.status == 'blocked'
            )
        ).options(joinedload(Person.friends)).distinct()
    )
    return list(result.scalars().unique().all())
