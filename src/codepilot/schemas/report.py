"""Structured investigation report, with claims labeled by evidentiary status."""

from typing import Literal

from pydantic import BaseModel


class InvestigationReport(BaseModel):
    observed_facts: list[str]
    hypotheses: list[str]
    root_cause: str | None
    confidence: Literal["low", "medium", "high"]
