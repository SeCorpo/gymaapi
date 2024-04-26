import logging

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from dto.personDTO import PersonDTO
from model.Person import Person


async def add_person(db: AsyncSession, user_id: int, person_dto: PersonDTO) -> Person:
    """ Add personal information to a user"""
    if user_id is None:
        raise HTTPException(status_code=401, detail="User not found")

    try:
        new_person = Person(
            first_name=person_dto.first_name,
            last_name=person_dto.last_name,
            date_of_birth=person_dto.date_of_birth,
            sex=person_dto.sex,
            city=person_dto.city,
            profile_text=person_dto.profile_text,
            gyma_share=person_dto.gyma_share,
        )
        db.add(new_person)
        await db.commit()
        await db.refresh(new_person)
        return new_person
    except Exception as e:
        await db.rollback()
        logging.error(e)
        raise HTTPException(status_code=500, detail="Something went wrong, unable to add person")
