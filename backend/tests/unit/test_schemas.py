import pytest
from pydantic import ValidationError

from app.domain.schemas import BriefResult


def build_payload(**overrides: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "summary": "Build a polished SaaS landing page.",
        "goals": ["Explain the product", "Collect qualified leads"],
        "deliverables": ["Landing page copy", "SEO-ready section map"],
        "constraints": ["Two-week timeline", "Limited budget"],
        "risks": [
            {
                "risk": "Scope may grow during copy review",
                "severity": "medium",
                "reason": "The brief asks for both design and copy outputs.",
            }
        ],
        "clarifying_questions": ["Which conversion event matters most?"],
        "recommended_next_action": "Confirm target audience and CTA priority.",
    }
    payload.update(overrides)
    return payload


def test_brief_result_accepts_valid_payload() -> None:
    result = BriefResult.model_validate(build_payload())

    assert result.risks[0].severity == "medium"


def test_brief_result_rejects_invalid_severity() -> None:
    with pytest.raises(ValidationError):
        BriefResult.model_validate(
            build_payload(risks=[{"risk": "x", "severity": "critical", "reason": "y"}])
        )


def test_brief_result_rejects_empty_goals() -> None:
    with pytest.raises(ValidationError):
        BriefResult.model_validate(build_payload(goals=[]))


def test_brief_result_requires_questions_to_end_with_question_mark() -> None:
    with pytest.raises(ValidationError):
        BriefResult.model_validate(build_payload(clarifying_questions=["Need audience details"]))


def test_brief_result_ignores_extra_fields() -> None:
    result = BriefResult.model_validate(build_payload(extra_field="ignored"))

    assert not hasattr(result, "extra_field")
