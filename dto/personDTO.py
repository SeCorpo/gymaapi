from datetime import date

from pydantic import BaseModel, Field


class PersonDTO(BaseModel):
    first_name: str = Field(..., description="First name")
    last_name: str = Field(..., description="Last name")
    date_of_birth: date = None
    sex: str = Field(..., description="Sex")
    # country: str = Field(...)
    city: str = None
    profile_text: str = None


class PersonSimpleDTO(BaseModel):
    full_name: str
    sex: str

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"
