import logging
from datetime import date

from sqlalchemy import select, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import joinedload

from model.Friendship import Friendship
from model.Person import Person


async def get_friends_by_person_id(db: AsyncSession, person_id: int) -> list[Person]:
    """ Get all friends for a given person by their person_id. """
    result = await db.execute(
        select(Person).join(Friendship, or_(
            Friendship.person_id == person_id,
            Friendship.friend_id == person_id
        )).where(or_(
            and_(Friendship.person_id == person_id, Person.person_id == Friendship.friend_id),
            and_(Friendship.friend_id == person_id, Person.person_id == Friendship.person_id)
        )).options(joinedload(Person.friends)).distinct()
    )
    return list(result.scalars().all())


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


async def update_friendship_status(db: AsyncSession, person_id: int, friend_id: int, status: str) -> bool:
    """ Update the status of a friendship. """
    try:
        result = await db.execute(
            select(Friendship).where(
                or_(
                    and_(Friendship.person_id == person_id, Friendship.friend_id == friend_id),
                    and_(Friendship.person_id == friend_id, Friendship.friend_id == person_id)
                )
            )
        )
        friendship = result.scalar_one_or_none()

        if friendship:
            friendship.status = status
            await db.commit()
            await db.refresh(friendship)
            return True
        else:
            return False
    except NoResultFound:
        return False
    except Exception as e:
        await db.rollback()
        logging.error(f"Failed to update friendship status: {e}")
        return False


async def remove_friendship(db: AsyncSession, person_id: int, friend_id: int) -> bool:
    """ Remove a friendship. """
    try:
        result = await db.execute(
            select(Friendship).where(
                or_(
                    and_(Friendship.person_id == person_id, Friendship.friend_id == friend_id),
                    and_(Friendship.person_id == friend_id, Friendship.friend_id == person_id)
                )
            )
        )
        friendship = result.scalar_one_or_none()

        if friendship:
            await db.delete(friendship)
            await db.commit()
            return True
        else:
            return False
    except NoResultFound:
        return False
    except Exception as e:
        await db.rollback()
        logging.error(f"Failed to remove friendship: {e}")
        return False


async def get_pending_friendships(db: AsyncSession, person_id: int) -> list[Person]:
    """ Get all persons involved in pending friendships for a given person. """
    result = await db.execute(
        select(Person).join(Friendship, or_(
            Friendship.person_id == person_id,
            Friendship.friend_id == person_id
        )).where(
            and_(
                or_(
                    Friendship.person_id == person_id,
                    Friendship.friend_id == person_id
                ),
                Friendship.status == 'pending'
            )
        ).options(joinedload(Person.friends)).distinct()
    )
    return list(result.scalars().all())
