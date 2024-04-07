import datetime
from typing import List

from pydantic import BaseModel, Field

from dto import exerciseDTO


class GymaPubDTO(BaseModel):
    person_name: str = Field(default='Anon Gymbro')
    time_of_arrival: datetime = Field(...)
    time_of_leaving: datetime = Field(...)
    exercises: List[exerciseDTO] = Field(...)

