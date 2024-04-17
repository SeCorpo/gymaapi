from pydantic import BaseModel, Field


class ExerciseDTO(BaseModel):
    exercise_name: str
    exercise_type: str
    count: int = Field(default=None)
    sets: int = Field(default=None)
    weight: float = Field(default=None)
    minutes: int = Field(default=None)
    km: float = Field(default=None)
    level: int = Field(default=None)
    description: str = Field(default=None)
