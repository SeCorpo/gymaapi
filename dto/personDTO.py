from datetime import date
from typing import Optional

from pydantic import BaseModel


class PersonDTO(BaseModel):
    profile_url: str
    first_name: str
    last_name: str
    date_of_birth: date
    sex: str
    city: Optional[str] = None
    profile_text: Optional[str] = None
    pf_path_l: Optional[str] = None
    pf_path_m: Optional[str] = None


class PersonSimpleDTO(BaseModel):
    """ For use on non-personal request (e.q. gymas, not profile). """
    profile_url: str
    full_name: str
    sex: str
    pf_path_m: Optional[str] = None

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"
