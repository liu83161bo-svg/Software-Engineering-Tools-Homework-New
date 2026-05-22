#!/usr/bin/env python3
"""Safety tests: format compliance, refusal correctness, tool blocking, schema validation."""
import pytest
import json
import yaml
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.tool_validator import validate_tool_call

# Load red-team inputs
REDTEAM_PATH = Path(__file__).parent / "redteam" / "adversarial_inputs.yaml"
with open(REDTEAM_PATH) as f:
    adversarial_inputs = yaml.safe_load(f)

#### Test 1: Format compliance (input must be valid JSON) ####
def test_format_compliance():
    """SG-1: Non-JSON input must be rejected."""
    from src.tool_validator import validate_tool_call
    # Simulate a non-JSON input (string instead of dict)
    result, msg = validate_tool_call("classify_eeg", "not a dict")
    assert result == False, f"Expected rejection for non-dict parameters, got {result}"
    assert msg is not None

#### Test 2: Refusal correctness – unauthorized tool ####
def test_refusal_unauthorized_tool():
    """SG-2: Calling a tool not in allowlist must be refused."""
    result, msg = validate_tool_call("delete_all", {})
    assert result == False
    assert "not in allowlist" in msg

#### Test 3: Refusal correctness – missing required parameter ####
def test_refusal_missing_required():
    """SG-3: Missing required field 'signal' must be refused."""
    result, msg = validate_tool_call("classify_eeg", {"subject_id": "sub001"})
    assert result == False
    assert "Missing required field" in msg

#### Test 4: Tool blocking – parameter type violation ####
def test_tool_blocking_parameter_type():
    """SG-4: Wrong parameter type must be blocked."""
    result, msg = validate_tool_call("classify_eeg", {"signal": "abc"})
    assert result == False
    assert "should be array" in msg

#### Test 5: Schema validation – array length ####
def test_schema_validation_array_length():
    """SG-5: Signal array length not equal to 1000 must be rejected."""
    short_signal = [0.0] * 500
    result, msg = validate_tool_call("classify_eeg", {"signal": short_signal})
    assert result == False
    assert "Array too short" in msg

#### Parameterized test from red-team inputs ####
@pytest.mark.parametrize("test_case", adversarial_inputs, ids=lambda tc: tc["id"])
def test_redteam_input(test_case):
    """Run all red-team adversarial inputs through validation."""
    tool = test_case["input"]["tool"]
    params = test_case["input"]["parameters"]
    result, msg = validate_tool_call(tool, params)
    expected_blocked = test_case["expected"] == "tool_blocked"
    assert result != expected_blocked, (
        f"Test {test_case['id']}: expected blocked={expected_blocked}, "
        f"actual blocked={not result}. Message: {msg}"
    )