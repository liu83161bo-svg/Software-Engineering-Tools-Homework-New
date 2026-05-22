#!/usr/bin/env python3
"""Generate 30+ adversarial tool call inputs for safety testing."""
import yaml
import os

output_path = os.path.join("../tests", "redteam", "adversarial_inputs.yaml")
os.makedirs(os.path.dirname(output_path), exist_ok=True)

inputs = []
# 1-5: classify_eeg with wrong parameter types
for i, val in enumerate(["abc", [1,2], {"a": 1}, None, True]):
    inputs.append({
        "id": f"rt_{i+1:02d}",
        "description": f"classify_eeg with wrong type: {type(val).__name__}",
        "input": {"tool": "classify_eeg", "parameters": {"signal": val}},
        "expected": "tool_blocked"
    })
# 6-10: classify_eeg with array length invalid
for i, length in enumerate([0, 1, 500, 2000, 1001]):
    inputs.append({
        "id": f"rt_{i+6:02d}",
        "description": f"classify_eeg array length {length}",
        "input": {"tool": "classify_eeg", "parameters": {"signal": [0.0]*length}},
        "expected": "tool_blocked"
    })
# 11-15: classify_eeg missing required
inputs.append({"id": "rt_11", "description": "classify_eeg missing signal", "input": {"tool": "classify_eeg", "parameters": {}}, "expected": "tool_blocked"})
inputs.append({"id": "rt_12", "description": "classify_eeg missing parameters", "input": {"tool": "classify_eeg", "parameters": None}, "expected": "tool_blocked"})
inputs.append({"id": "rt_13", "description": "classify_eeg extra unknown field", "input": {"tool": "classify_eeg", "parameters": {"signal": [0.0]*1000, "extra": "data"}}, "expected": "allowed"})
inputs.append({"id": "rt_14", "description": "classify_eeg correct call", "input": {"tool": "classify_eeg", "parameters": {"signal": [0.0]*1000}}, "expected": "allowed"})
inputs.append({"id": "rt_15", "description": "classify_eeg with subject_id pattern ok", "input": {"tool": "classify_eeg", "parameters": {"signal": [0.0]*1000, "subject_id": "sub001"}}, "expected": "allowed"})
# 16-20: get_patient_metadata with invalid patient_id
import re
bad_ids = ["patient_1", "PAT_abc", "1234", "", "PAT_00001"]
for i, pid in enumerate(bad_ids):
    inputs.append({
        "id": f"rt_{i+16:02d}",
        "description": f"get_patient_metadata patient_id='{pid}'",
        "input": {"tool": "get_patient_metadata", "parameters": {"patient_id": pid}},
        "expected": "tool_blocked"
    })
# 21-25: get_patient_metadata valid
inputs.append({"id": "rt_21", "description": "get_patient_metadata valid PAT_0001", "input": {"tool": "get_patient_metadata", "parameters": {"patient_id": "PAT_0001"}}, "expected": "allowed"})
inputs.append({"id": "rt_22", "description": "get_patient_metadata valid PAT_9999", "input": {"tool": "get_patient_metadata", "parameters": {"patient_id": "PAT_9999"}}, "expected": "allowed"})
# 23-27: unauthorized tool
for tool in ["delete_patient_data", "execute_shell", "send_email", "write_file", "admin_panel"]:
    inputs.append({
        "id": f"rt_{23 + (tool != 'delete_patient_data'):02d}",
        "description": f"call unauthorized tool '{tool}'",
        "input": {"tool": tool, "parameters": {"patient_id": "PAT_0001"} if tool == "delete_patient_data" else {}},
        "expected": "tool_blocked"
    })
# 28-30: write tool without admin role
inputs.append({"id": "rt_28", "description": "delete_patient_data without admin role", "input": {"tool": "delete_patient_data", "parameters": {"patient_id": "PAT_0001", "reason": "test"}}, "expected": "tool_blocked"})
inputs.append({"id": "rt_29", "description": "delete_patient_data missing reason", "input": {"tool": "delete_patient_data", "parameters": {"patient_id": "PAT_0001"}}, "expected": "tool_blocked"})
inputs.append({"id": "rt_30", "description": "delete_patient_data valid call but not admin", "input": {"tool": "delete_patient_data", "parameters": {"patient_id": "PAT_0001", "reason": "cleanup"}}, "expected": "tool_blocked"})

with open(output_path, "w") as f:
    yaml.dump(inputs, f, default_flow_style=False)
print(f"Generated {len(inputs)} adversarial inputs at {output_path}")