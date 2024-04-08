from pydantic import BaseModel, Field


class PersonDTO(BaseModel):
    first_name: str = Field(...)
    last_name: str = Field(...)
    country: str = Field(...)
    city: str = Field(...)
