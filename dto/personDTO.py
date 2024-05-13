from datetime import date

from pydantic import BaseModel, Field


class PersonDTO(BaseModel):
    first_name: str
    last_name: str
    date_of_birth: date
    sex: str
    # country: str = Field(...)
    city: str = None
    profile_text: str = None


class PersonSimpleDTO(BaseModel):
    full_name: str
    sex: str

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"
