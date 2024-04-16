from datetime import datetime
from typing import List

from pydantic import BaseModel, Field

from dto.exerciseDTO import ExerciseDTO
from dto.personDTO import PersonDTO


class GymaDTO(BaseModel):
    gyma_id: int = Field(...)
    person: PersonDTO = Field(...)
    time_of_arrival: datetime = Field(...)
    time_of_leaving: datetime = Field(default=None)
    exercises: List[ExerciseDTO] = Field(default=None)

