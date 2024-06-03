import logging

from sqlalchemy import select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from dto.personDTO import EnterPersonDTO
from model.Person import Person


async def get_person_by_user_id(db: AsyncSession, user_id: int) -> Person | None:
    """ Get Person object by user id. """
    try:
        result = await db.execute(select(Person).filter_by(person_id=user_id))
        person = result.scalar_one()
        return person
    except NoResultFound:
        return None


async def get_person_by_profile_url(db: AsyncSession, profile_url: str) -> Person | None:
    """ Get Person object by profile url. """
    try:
        result = await db.execute(select(Person).filter_by(profile_url=profile_url))
        person = result.scalar_one()
        return person
    except NoResultFound:
        return None


async def add_person(db: AsyncSession, user_id: int, enter_person_dto: EnterPersonDTO) -> Person | None:
    """ Add personal information of a user. """
    if user_id is None:
        return None

    try:
        unique_profile_url_fullname = await generate_unique_profile_url(db,
                                                                        enter_person_dto.first_name,
                                                                        enter_person_dto.last_name)

        new_person = Person(
            person_id=user_id,
            profile_url=unique_profile_url_fullname,
            first_name=enter_person_dto.first_name,
            last_name=enter_person_dto.last_name,
            date_of_birth=enter_person_dto.date_of_birth,
            sex=enter_person_dto.sex,
            city=enter_person_dto.city,
            profile_text=enter_person_dto.profile_text,
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


async def edit_person(db: AsyncSession, user_id: int, person: Person, enter_person_dto: EnterPersonDTO) -> Person | None:
    """ Edit personal information of a user. """
    if user_id is None:
        return None

    try:
        person.first_name = enter_person_dto.first_name
        person.last_name = enter_person_dto.last_name
        person.date_of_birth = enter_person_dto.date_of_birth
        person.sex = enter_person_dto.sex
        person.city = enter_person_dto.city
        person.profile_text = enter_person_dto.profile_text

        await db.commit()
        await db.refresh(person)
        return person
    except Exception as e:
        await db.rollback()
        logging.error(f"Failed to update person: {e}")
        return None


async def set_pf_paths(db: AsyncSession, person: Person, pf_path_l: str, pf_path_m: str) -> Person | None:
    """ Set or replace pf_path_l and pf_path_m of person object. """
    try:
        person.pf_path_l = pf_path_l
        person.pf_path_m = pf_path_m

        await db.commit()
        await db.refresh(person)
        return person
    except Exception as e:
        await db.rollback()
        logging.error(f"Failed to set or change pf_paths: {e}")
        return None


async def generate_unique_profile_url(db: AsyncSession, first_name: str, last_name: str) -> str:
    """Generate a unique profile URL based on full name, by adding a count to it."""
    base_profile_url = f"{first_name.lower()}{last_name.lower()}"
    max_chars = 32
    max_base_length = max_chars - len(str(max_chars))
    base_profile_url = base_profile_url[:max_base_length]

    profile_url = base_profile_url
    count = 1
    while True:
        if await check_profile_url_available(db, profile_url):
            return profile_url
        count_str = str(count)
        max_count_length = max_chars - len(base_profile_url)
        count_str = count_str[:max_count_length]
        profile_url = f"{base_profile_url}{count_str}"
        count += 1


async def check_profile_url_available(db: AsyncSession, profile_url: str) -> bool:
    """Check if profile url is available."""
    async with db.begin():
        result = await db.execute(select(Person).filter_by(profile_url=profile_url))
        return not bool(result.scalar_one_or_none())
