from pydantic import BaseModel, Field


class SessionDataObject(BaseModel):
    session_id: str | None = Field(default=None, description="Session ID for later use maybe")
    user_id: int
    gyma_id: int | None = Field(default=None, description="The ID of the gyma associated with the session")
