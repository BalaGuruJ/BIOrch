import pytest
from pydantic import ValidationError
from biorch.core.result import Result, ResultStatus

def test_result_construction():
    """
    Test valid Result construction.
    """
    result = Result(task_id="t1", status=ResultStatus.SUCCESS)
    assert result.task_id == "t1"
    assert result.status == ResultStatus.SUCCESS

def test_result_invalid_status():
    """
    Test Result rejects invalid status values.
    """
    with pytest.raises(ValidationError):
        Result(task_id="t1", status="invalid_status")

def test_result_serialization():
    """
    Test Result serialization/deserialization.
    """
    result = Result(task_id="t1", status=ResultStatus.PARTIAL, findings=[{"key": "value"}])
    assert Result.model_validate_json(result.model_dump_json()) == result
