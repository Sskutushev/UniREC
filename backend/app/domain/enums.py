from enum import StrEnum


class Severity(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class RunStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class ErrorCode(StrEnum):
    PROVIDER_FAILURE = "provider_failure"
    VALIDATION_ERROR = "validation_error"
    RUN_NOT_FOUND = "run_not_found"
    INTERNAL_ERROR = "internal_error"
