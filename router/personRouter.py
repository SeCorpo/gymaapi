import logging
import os

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from dto.imageDTO import ImageDTO
from dto.personDTO import PersonDTO, EnterPersonDTO
from provider.authProvider import get_auth_key
from provider.imageProvider import process_image, move_images_to_archive
from service.personService import add_person, get_person_by_user_id, edit_person, set_pf_paths
from session.sessionService import get_user_id_from_session_data

router = APIRouter(prefix="/api/v1/person", tags=["person"])
API_URL = os.getenv("API_BASE_URL")


@router.post("/", response_model=PersonDTO, status_code=200)
async def add_or_edit_person(enter_person_dto: EnterPersonDTO,
                             auth_token: str | None = Depends(get_auth_key),
                             db: AsyncSession = Depends(get_db)):
    logging.info("Creating or editing person object for user")

    user_id = await get_user_id_from_session_data(auth_token)
    if user_id is None:
        raise HTTPException(status_code=401, detail="Session invalid")
    else:
        person = await get_person_by_user_id(db, user_id)
        if person is None:
            logging.info("Creating person object for user")
            new_person = await add_person(db, user_id, enter_person_dto)
            if new_person is None:
                raise HTTPException(status_code=500, detail="Person cannot be created")
            else:
                return PersonDTO(
                    profile_url=new_person.profile_url,
                    first_name=new_person.first_name,
                    last_name=new_person.last_name,
                    date_of_birth=new_person.date_of_birth,
                    sex=new_person.sex,
                    city=new_person.city,
                    profile_text=new_person.profile_text,
                    pf_path_l=new_person.pf_path_l,
                    pf_path_m=new_person.pf_path_m,
                )
        else:
            logging.info("Updating person object for user")
            edited_person = await edit_person(db, user_id, person, enter_person_dto)
            if edited_person is None:
                raise HTTPException(status_code=500, detail="Person cannot be updated")
            else:
                return PersonDTO(
                    profile_url=edited_person.profile_url,
                    first_name=edited_person.first_name,
                    last_name=edited_person.last_name,
                    date_of_birth=edited_person.date_of_birth,
                    sex=edited_person.sex,
                    city=edited_person.city,
                    profile_text=edited_person.profile_text,
                    pf_path_l=edited_person.pf_path_l,
                    pf_path_m=edited_person.pf_path_m,
                )


@router.post("/picture", response_model=PersonDTO, status_code=200)
async def upload_picture(
    file: UploadFile = File(...),
    auth_token: str | None = Depends(get_auth_key),
    db: AsyncSession = Depends(get_db)
):
    logging.info("Processing picture for user")

    try:
        image_dto = ImageDTO(file=file)
        image_dto.validate_file(file)  # Perform validation
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=e.errors())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    user_id = await get_user_id_from_session_data(auth_token)
    if user_id is None:
        raise HTTPException(status_code=401, detail="Session invalid")

    person = await get_person_by_user_id(db, user_id)
    if person is None:
        raise HTTPException(status_code=404, detail="Picture cannot be added if there is no person")

    if person.pf_path_l and person.pf_path_m is not None:
        logging.info("Archiving previous picture of user")
        move_ok = move_images_to_archive(person.pf_path_l, person.pf_path_m)
        if not move_ok:
            raise HTTPException(status_code=500, detail="Picture cannot be moved to archive")

    picture_names = process_image(image_dto)
    if picture_names is None:
        raise HTTPException(status_code=500, detail="Picture cannot be processed, please try a different picture")

    person_with_pf_paths = await set_pf_paths(db, person, picture_names["pf_path_l"], picture_names["pf_path_m"])
    if not person_with_pf_paths:
        raise HTTPException(status_code=500, detail="New pictures cannot be added to person")

    return PersonDTO(
        profile_url=person_with_pf_paths.profile_url,
        first_name=person_with_pf_paths.first_name,
        last_name=person_with_pf_paths.last_name,
        date_of_birth=person_with_pf_paths.date_of_birth,
        sex=person_with_pf_paths.sex,
        city=person_with_pf_paths.city,
        profile_text=person_with_pf_paths.profile_text,
        pf_path_l=f"{API_URL}/images/large/{person_with_pf_paths.pf_path_l}",
        pf_path_m=f"{API_URL}/images/medium/{person_with_pf_paths.pf_path_m}",
    )
