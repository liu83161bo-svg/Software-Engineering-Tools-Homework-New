# Safety & Privacy Policy – LFP Age Classification System

## 1. Scope
This policy applies to all components of the LFP Age Classification system: data ingestion, model training, inference API, and monitoring. It covers data handling, tool usage, output validation, and incident response.

## 2. Permitted Use
- Academic research on brain-age prediction.
- Internal model development and benchmarking.
- Authorized clinical studies with ethical approval.

## 3. Prohibited Use
- Clinical diagnosis or treatment decisions.
- Individual identification beyond anonymized IDs.
- Discrimination based on age, health, or other protected attributes.
- Any use without documented ethical approval.

## 4. Data Minimization & Anonymization
- Only collect fields required for age classification: `lfpN` signal, `par/Age`, anonymized subject ID.
- All PII (names, addresses, device IDs) must be stripped before storage.
- Apply `src/anonymize.py` to raw data before ingestion.

## 5. Retention & Deletion
- Raw .mat files retained for maximum 10 years, then automatically deleted.
- Golden set retained for 3 years; older versions archived.
- Logs retained for 90 days; full request payloads retained 7 days in debug mode only.

## 6. Logging Policy
- Log structured metadata: request ID, latency, error codes, tool calls.
- Raw signal values are logged only in debug mode (separate log file, rotated daily).
- PII is redacted at the application boundary before logging.

## 7. Refusal Behavior
When input does not meet validation criteria (schema violation, out-of-range values, unauthorized tool), the system must:
- Return a structured error code (e.g., `ERR_INVALID_INPUT`, `ERR_TOOL_BLOCKED`).
- Never execute the action.
- Log the refusal reason for audit.

## 8. Uncertainty Handling
If model confidence < 0.6, output is flagged as `low_confidence` and routed to human review. The API returns the prediction but with a warning field.

## 9. Tool Use Controls
- Only tools listed in `configs/tool_allowlist.yaml` may be called.
- Each tool has required parameter schema (JSON Schema) and permission level.
- Destructive actions (e.g., delete) require explicit confirmation.

## 10. Ownership
| Role | Owner |
|------|-------|
| Policy decisions | Product Owner (name) |
| Security controls | Security Engineer (name) |
| Implementation | ML Engineer (name) |
| Incident response | On-call rotation (team) |

*Policy version 1.0 – effective 2026-02-15*