from typing import List
from fastapi import APIRouter, Depends
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db

from dto.gymaDTO import GymaDTO
from service.pubService import get_last_three_gyma_entry

router = APIRouter(prefix="/api/v1/pub", tags=["pub"])


@router.get("/", response_model=List[GymaDTO], status_code=200)
async def get_pub(gyma_keys: str = None, db: AsyncSession = Depends(get_db)):
    logging.info(f"Searching for the latest three gyma entries {'excluding: ' + gyma_keys if gyma_keys else ''}")

    return await get_last_three_gyma_entry(gyma_keys, db)
