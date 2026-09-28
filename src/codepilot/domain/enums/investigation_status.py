"""Lifecycle states for an investigation."""

from enum import StrEnum

class InvestigationStatus(StrEnum):
    PENDING = "pending"
    PLANNING = "planning"
    COLLECTING_EVIDENCE = "collecting_evidence"
    ANALYZING = "analyzing"
    AWAITING_APPROVAL = "awaiting_approval"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
