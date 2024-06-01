from typing import Optional

from pydantic import BaseModel, EmailStr, Field

from dto.personDTO import PersonDTO


class LoginDTO(BaseModel, frozen=True):
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="User password")


class LoginResponseDTO(BaseModel):
    session_token: str
    personDTO: Optional[PersonDTO] = None
