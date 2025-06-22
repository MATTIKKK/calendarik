from pydantic import BaseModel


class UpdatePersonalityRequest(BaseModel):
    personality: str