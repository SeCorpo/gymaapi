import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from dto.personDTO import PersonDTO
from provider.authProvider import get_auth_key
from service.personService import add_person, get_person_by_user_id, edit_person
from session.sessionService import get_user_id_from_session_data

router = APIRouter(prefix="/api/v1/person", tags=["person"])


@router.post("/", response_model=PersonDTO, status_code=200)
async def add_or_edit_person(person_dto: PersonDTO,
                             auth_token: str | None = Depends(get_auth_key),
                             db: AsyncSession = Depends(get_db)):
    logging.info("Creating or editing person object for user")

    user_id = await get_user_id_from_session_data(auth_token)
    if user_id is None:
        raise HTTPException(status_code=401, detail="Session invalid")
    else:
        person = await get_person_by_user_id(db, user_id)
        if person is None:
            new_person = await add_person(db, user_id, person_dto)
            if new_person is None:
                raise HTTPException(status_code=500, detail="Person cannot be created")
            else:
                response_person_dto = PersonDTO(
                    first_name=new_person.first_name,
                    last_name=new_person.last_name,
                    date_of_birth=new_person.date_of_birth,
                    sex=new_person.sex,
                    city=new_person.city,
                    profile_text=new_person.profile_text,
                )
                return response_person_dto
        else:
            edited_person = await edit_person(db, user_id, person, person_dto)
            if edited_person is None:
                raise HTTPException(status_code=500, detail="Person cannot be updated")
            else:
                response_person_dto = PersonDTO(
                    first_name=edited_person.first_name,
                    last_name=edited_person.last_name,
                    date_of_birth=edited_person.date_of_birth,
                    sex=edited_person.sex,
                    city=edited_person.city,
                    profile_text=edited_person.profile_text,
                )
                return response_person_dto
