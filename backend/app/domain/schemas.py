from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.domain.enums import RunStatus, Severity


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="ignore", str_strip_whitespace=True, use_enum_values=True)


class Risk(StrictModel):
    risk: str = Field(min_length=1)
    severity: Severity
    reason: str = Field(min_length=1)


class BriefResult(StrictModel):
    summary: str = Field(min_length=1)
    goals: list[str] = Field(min_length=1)
    deliverables: list[str] = Field(min_length=1)
    constraints: list[str] = Field(min_length=1)
    risks: list[Risk] = Field(min_length=1)
    clarifying_questions: list[str] = Field(min_length=1)
    recommended_next_action: str = Field(min_length=1)

    @field_validator("goals", "deliverables", "constraints", "clarifying_questions")
    @classmethod
    def validate_string_list(cls, value: list[str]) -> list[str]:
        if any(not item.strip() for item in value):
            raise ValueError("list items must be non-empty")
        return value

    @field_validator("clarifying_questions")
    @classmethod
    def validate_questions(cls, value: list[str]) -> list[str]:
        if any(not item.endswith("?") for item in value):
            raise ValueError("clarifying questions must end with '?' ")
        return value


class DecodeBriefRequest(StrictModel):
    text: str = Field(min_length=50, max_length=10000)


class DecodeRunCreate(StrictModel):
    input_text: str = Field(min_length=1)
    input_hash: str = Field(min_length=64, max_length=64)
    provider_name: str = Field(min_length=1)
    status: RunStatus = RunStatus.PENDING


class DecodeRunResponse(StrictModel):
    run_id: UUID
    status: RunStatus
    result: BriefResult | None = None
    error_code: str | None = None
    error_message: str | None = None
    created_at: datetime
    updated_at: datetime
    completed_at: datetime | None = None


class DecodeRunStatus(DecodeRunResponse):
    input_text: str
    provider_name: str | None = None


class ErrorResponse(StrictModel):
    error_code: str
    message: str
