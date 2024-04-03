from pydantic import BaseModel, EmailStr, Field


class LoginDTO(BaseModel, frozen=True):
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="User password")
