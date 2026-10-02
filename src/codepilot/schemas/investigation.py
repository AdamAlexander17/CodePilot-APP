"""Pydantic schemas for the investigation API (request/response shapes)."""

import uuid
from datetime import datetime

from pydantic import BaseModel , ConfigDict
from codepilot.domain.enums.investigation_status import InvestigationStatus

class InvestigationCreate(BaseModel):
    title: str
    repo_path: str


class InvestigationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    repo_path: str
    status: InvestigationStatus
    result: str | None
    created_at: datetime
    updated_at: datetime
