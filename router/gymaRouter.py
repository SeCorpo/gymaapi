from fastapi import APIRouter
import logging


router = APIRouter(prefix="/gyma", tags=["gyma"])


@router.post("/start", status_code=201)
def start_gyma(
    # person id from session
):
    return
