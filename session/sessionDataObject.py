from datetime import datetime
from pydantic import BaseModel, Field


class SessionDataObject(BaseModel):
    session_id: str = Field(default=None, description="Session ID for later use maybe")
    person_id: int = Field(..., description="The ID of the person associated with the session")
    gyma_id: int = Field(default=None, description="The ID of the gyma associated with the session")
    # created_at: datetime = Field(default_factory=datetime.now, description="Session creation timestamp")
