import logging

from sqlalchemy import select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from dto.personDTO import PersonDTO
from model.Person import Person


async def get_person_by_user_id(db: AsyncSession, user_id: int) -> Person | None:
    try:
        result = await db.execute(select(Person).filter_by(person_id=user_id))
        person = result.scalar_one()
        return person
    except NoResultFound:
        return None


async def add_person(db: AsyncSession, user_id: int, person_dto: PersonDTO) -> Person | None:
    """ Add personal information of a user. """
    if user_id is None:
        return None

    try:
        new_person = Person(
            person_id=user_id,
            first_name=person_dto.first_name,
            last_name=person_dto.last_name,
            date_of_birth=person_dto.date_of_birth,
            sex=person_dto.sex,
            city=person_dto.city,
            profile_text=person_dto.profile_text,
            # gyma_share=person_dto.gyma_share,
        )
        db.add(new_person)
        await db.commit()
        await db.refresh(new_person)
        return new_person
    except Exception as e:
        await db.rollback()
        logging.error(e)
        return None


async def edit_person(db: AsyncSession, user_id: int, person: Person, person_dto: PersonDTO) -> Person | None:
    """ Edit personal information of a user. """
    if user_id is None:
        return None

    try:
        person.first_name = person_dto.first_name
        person.last_name = person_dto.last_name
        person.date_of_birth = person_dto.date_of_birth
        person.sex = person_dto.sex
        person.city = person_dto.city
        person.profile_text = person_dto.profile_text
        # person.gyma_share = person_dto.gyma_share

        await db.commit()
        await db.refresh(person)
        return person
    except Exception as e:
        await db.rollback()
        logging.error(f"Failed to update person: {e}")
        return None
