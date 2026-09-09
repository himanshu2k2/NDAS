import pytest
from fastapi import HTTPException

from app.services.affidavit_service import _validate_and_coerce_variables

VARIABLE_SPECS = [
    {"key": "recipient_name", "label": "Recipient Name", "type": "text", "required": True, "options": None},
    {"key": "recipient_age", "label": "Recipient Age", "type": "number", "required": True, "options": None},
    {"key": "remarks", "label": "Remarks", "type": "textarea", "required": False, "options": None},
]


def test_missing_required_variable_raises_422() -> None:
    with pytest.raises(HTTPException) as exc_info:
        _validate_and_coerce_variables(VARIABLE_SPECS, {"recipient_age": 52})
    assert exc_info.value.status_code == 422
    assert "recipient_name" in exc_info.value.detail


def test_unexpected_variable_raises_400() -> None:
    with pytest.raises(HTTPException) as exc_info:
        _validate_and_coerce_variables(
            VARIABLE_SPECS, {"recipient_name": "ABC", "recipient_age": 52, "donor_name": "XYZ"}
        )
    assert exc_info.value.status_code == 400
    assert "donor_name" in exc_info.value.detail


def test_optional_variable_defaults_to_empty_string_when_absent() -> None:
    result = _validate_and_coerce_variables(VARIABLE_SPECS, {"recipient_name": "ABC", "recipient_age": 52})
    assert result["remarks"] == ""


def test_number_type_is_coerced_to_int_or_float() -> None:
    result = _validate_and_coerce_variables(
        VARIABLE_SPECS, {"recipient_name": "ABC", "recipient_age": "52"}
    )
    assert result["recipient_age"] == 52
    assert isinstance(result["recipient_age"], int)


def test_non_numeric_value_for_number_field_raises_422() -> None:
    with pytest.raises(HTTPException) as exc_info:
        _validate_and_coerce_variables(VARIABLE_SPECS, {"recipient_name": "ABC", "recipient_age": "not-a-number"})
    assert exc_info.value.status_code == 422
