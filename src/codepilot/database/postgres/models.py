"""SQLAlchemy ORM models for the Postgres platform database."""
from sqlalchemy.dialects.postgresql import JSONB

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from codepilot.domain.enums.investigation_status import InvestigationStatus

class Base(DeclarativeBase):
    pass

class Investigation(Base):
    __tablename__ = "investigations"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title: Mapped[str]
    repo_path: Mapped[str]
    status: Mapped[InvestigationStatus] = mapped_column(
        Enum(InvestigationStatus, values_callable=lambda enum_cls: [e.value for e in enum_cls]),
        default=InvestigationStatus.PENDING,
    )
    result: Mapped[str | None] = mapped_column(default=None)
    result_report: Mapped[dict | None] = mapped_column(JSONB, default=None)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)