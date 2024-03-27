from dataclasses import dataclass


@dataclass
class RegisterDTO:
    email: str
    password: str
    password2: str
