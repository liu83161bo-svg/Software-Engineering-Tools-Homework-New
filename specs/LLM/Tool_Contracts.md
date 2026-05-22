# Tool Contracts – LFP Classification Assistant

## Tool Allowlist

| Tool Name | Permission Level | Confirmation Required | Allowed Roles |
|-----------|------------------|------------------------|---------------|
| classify_eeg | read | No | all |
| get_patient_metadata | read | No | researcher, clinician |
| get_age_statistics | read | No | all |
| delete_patient_data | write | Yes (user must confirm in same session) | admin |
| retrieve_knowledge | read | No | all |

## Parameter Schemas

### classify_eeg
- `signal`: array of 1000 floats (required)
- `subject_id`: string matching `^sub\\d{3}$` (optional)

### get_patient_metadata
- `patient_id`: string matching `^PAT_\\d{4}$` (required)

### get_age_statistics
- `age_min`: integer (optional, default 0)
- `age_max`: integer (optional, default 47)

### delete_patient_data
- `patient_id`: string matching `^PAT_\\d{4}$` (required)
- `reason`: string, max length 500 (required)

## Confirmation Rules
- Write tools (`delete_patient_data`) require explicit user confirmation (e.g., "I confirm I want to delete data for PAT_0001.") before execution.
- The confirmation must occur within the same conversation session; expired after 10 minutes of inactivity.

## Error Handling
- Timeout: if a tool call exceeds 5 seconds, return a timeout error to the orchestrator and do not retry.
- Parameter validation failure: return specific error code (e.g., `ERR_INVALID_PARAM`) to the model.
- Tool unavailable: return `ERR_TOOL_UNAVAILABLE` and log the attempt.