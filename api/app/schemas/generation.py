import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class GenerationCreate(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=5000)


class GenerationResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    post_id: uuid.UUID | None
    prompt: str
    status: str
    model_usage: dict | None
    quality_scores: dict | None
    iterations: int
    duration_seconds: int | None
    error_message: str | None
    created_at: datetime
    completed_at: datetime | None
