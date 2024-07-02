import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from dto.personDTO import PersonDTO, PersonSimpleDTO
from dto.profileDTO import ProfileDTO
from provider.authProvider import get_auth_key_or_none, get_auth_key
from service.friendshipService import get_friends_by_person_id, get_friendship, add_friendship, remove_friendship, \
    get_friendship_of_requester, update_friendship_status
from service.personService import get_person_by_profile_url, get_person_by_user_id
from session.sessionService import get_user_id_from_session_data

router = APIRouter(prefix="/api/v1/profile", tags=["profile"])

#  get profile
#  request friendship (add friendship object with status pending)
#  remove request or friendship (excluding blocked status), also used for declining request
#  accept friendship (change status to accepted)
#  block friendship (request or already accepted)


@router.get("/{profile_url}", response_model=ProfileDTO, status_code=200)
async def get_profile(profile_url: str,
                      auth_token: str | None = Depends(get_auth_key_or_none),
                      db: AsyncSession = Depends(get_db)):
    logging.info("Get profile: %s", profile_url)

    person_by_profile_url = await get_person_by_profile_url(db, profile_url)
    if person_by_profile_url is None or person_by_profile_url.gyma_share == "solo":
        raise HTTPException(status_code=404, detail="Profile does not exist")

    friendship_status = None
    user_id = None

    if auth_token is not None:
        user_id_from_session = await get_user_id_from_session_data(auth_token)
        if user_id_from_session is not None:
            user_id = user_id_from_session

            friendship = await get_friendship(db, user_id, person_by_profile_url.person_id)
            if friendship is not None:
                if friendship.status == "pending":
                    if friendship.friend_id == user_id:
                        friendship_status = "received"
                    else:
                        friendship_status = "pending"
                else:
                    friendship_status = friendship.status

    if person_by_profile_url.gyma_share == "gymbros":
        if user_id is None:
            raise HTTPException(status_code=401, detail="Profile for friends")

        if friendship_status != "accepted":
            raise HTTPException(status_code=403, detail="Profile for friends")

    friends = await get_friends_by_person_id(db, person_by_profile_url.person_id)

    friend_list = [
        PersonSimpleDTO(
            profile_url=friend.profile_url,
            first_name=friend.first_name,
            last_name=friend.last_name,
            sex=friend.sex,
            pf_path_m=friend.pf_path_m
        )
        for friend in friends
    ]

    person_dto = PersonDTO(
        profile_url=person_by_profile_url.profile_url,
        first_name=person_by_profile_url.first_name,
        last_name=person_by_profile_url.last_name,
        date_of_birth=person_by_profile_url.date_of_birth,
        sex=person_by_profile_url.sex,
        city=person_by_profile_url.city,
        profile_text=person_by_profile_url.profile_text,
        pf_path_l=person_by_profile_url.pf_path_l,
        pf_path_m=person_by_profile_url.pf_path_m,
    )

    profile_dto = ProfileDTO(
        personDTO=person_dto,
        friend_list=friend_list,
        friendship_status=friendship_status
    )

    return profile_dto

# todo: how to handle pending friendship being send to client that is logged in.


@router.get("/request/{profile_url}", status_code=200)
async def add_friend_by_profile(profile_url: str,
                                auth_token: str | None = Depends(get_auth_key),
                                db: AsyncSession = Depends(get_db)):
    logging.info("Add friendship with profile url: %s", profile_url)

    user_id = await get_user_id_from_session_data(auth_token)
    if user_id is None:
        raise HTTPException(status_code=401, detail="Session invalid")
    requester_has_profile = await get_person_by_user_id(db, user_id)
    if requester_has_profile is None:
        raise HTTPException(status_code=401, detail="Make your own profile before adding gymbros")
    else:
        person_by_profile_url = await get_person_by_profile_url(db, profile_url)
        if person_by_profile_url is None:
            raise HTTPException(status_code=404, detail="Profile does not exist")
        if person_by_profile_url.gyma_share == "solo":
            raise HTTPException(status_code=404, detail="Profile not public")

        already_friend = await get_friendship(db, user_id, person_by_profile_url.person_id)
        if already_friend is not None:
            if already_friend.status == "accepted":
                raise HTTPException(status_code=403, detail="Friendship already accepted")
            if already_friend.status == "pending":
                raise HTTPException(status_code=403, detail="Already requested")
            if already_friend.status == "blocked":
                raise HTTPException(status_code=403, detail="Profile does not exist")

        else:
            friendship_ok = await add_friendship(db, user_id, person_by_profile_url.person_id)
            if friendship_ok:
                return True
            else:
                raise HTTPException(status_code=403, detail="Unable to add friend")


@router.get("/disconnect/{profile_url}", status_code=200)
async def remove_friend_by_profile(profile_url: str,
                                   auth_token: str | None = Depends(get_auth_key),
                                   db: AsyncSession = Depends(get_db)):
    logging.info("Remove friendship with profile url: %s", profile_url)

    user_id = await get_user_id_from_session_data(auth_token)
    if user_id is None:
        raise HTTPException(status_code=401, detail="Session invalid")
    requester_has_profile = await get_person_by_user_id(db, user_id)
    if requester_has_profile is None:
        raise HTTPException(status_code=401, detail="Make your own profile first")
    else:
        person_by_profile_url = await get_person_by_profile_url(db, profile_url)
        if person_by_profile_url is None:
            raise HTTPException(status_code=404, detail="Profile does not exist")

        friendship_exists = await get_friendship(db, user_id, person_by_profile_url.person_id)
        if friendship_exists is None:
            raise HTTPException(status_code=403, detail="Not a friend")
        if friendship_exists.status == "blocked":
            return True

        else:
            friendship_removed = await remove_friendship(db, friendship_exists)
            if friendship_removed:
                return True
            else:
                raise HTTPException(status_code=403, detail="Unable to remove friend")


@router.get("/accept/{profile_url}", status_code=200)
async def accept_friend_by_profile(profile_url: str,
                                   auth_token: str | None = Depends(get_auth_key),
                                   db: AsyncSession = Depends(get_db)):
    logging.info("Accept friendship request with profile url: %s", profile_url)

    user_id = await get_user_id_from_session_data(auth_token)
    if user_id is None:
        raise HTTPException(status_code=401, detail="Session invalid")
    requester_has_profile = await get_person_by_user_id(db, user_id)
    if requester_has_profile is None:
        raise HTTPException(status_code=401, detail="Make your own profile first")
    else:
        person_by_profile_url = await get_person_by_profile_url(db, profile_url)
        if person_by_profile_url is None:
            raise HTTPException(status_code=404, detail="Profile does not exist")

        friendship_to_be_accepted = await get_friendship_of_requester(db, person_by_profile_url.person_id, user_id)
        if friendship_to_be_accepted is None:
            raise HTTPException(status_code=403, detail="Friendship cannot be accepted")
        if friendship_to_be_accepted.status == "accepted":
            raise HTTPException(status_code=403, detail="Friendship already accepted")
        if friendship_to_be_accepted.status == "blocked":
            raise HTTPException(status_code=403, detail="Friendship cannot be accepted, Profile does not exist")

        else:  # or status pending
            friendship_accepted = await update_friendship_status(db, friendship_to_be_accepted, "accepted")
            if friendship_accepted:
                return True
            else:
                raise HTTPException(status_code=403, detail="Unable to accept friend")


@router.get("/block/{profile_url}", status_code=200)
async def block_friend_by_profile(profile_url: str,
                                  auth_token: str | None = Depends(get_auth_key),
                                  db: AsyncSession = Depends(get_db)):
    logging.info("Block friendship request with profile url: %s", profile_url)

    user_id = await get_user_id_from_session_data(auth_token)
    if user_id is None:
        raise HTTPException(status_code=401, detail="Session invalid")
    requester_has_profile = await get_person_by_user_id(db, user_id)
    if requester_has_profile is None:
        raise HTTPException(status_code=401, detail="Make your own profile first")
    else:
        person_by_profile_url = await get_person_by_profile_url(db, profile_url)
        if person_by_profile_url is None:
            raise HTTPException(status_code=404, detail="Profile does not exist")

        friendship_to_be_blocked = await get_friendship_of_requester(db, person_by_profile_url.person_id, user_id)
        if friendship_to_be_blocked is None:
            raise HTTPException(status_code=403, detail="Cannot block friendship before friendship is initiated")
        if friendship_to_be_blocked.status == "blocked":
            raise HTTPException(status_code=403, detail="Friendship already blocked")

        else:
            friendship_blocked = await update_friendship_status(db, friendship_to_be_blocked, "blocked")
            if friendship_blocked:
                return True
            else:
                raise HTTPException(status_code=500, detail="Unable to block person")
