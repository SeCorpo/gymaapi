from typing import Optional

from pydantic import BaseModel

from dto.personDTO import PersonDTO


class LoginResponseDTO(BaseModel):
    session_token: str
    personDTO: Optional[PersonDTO] = None
