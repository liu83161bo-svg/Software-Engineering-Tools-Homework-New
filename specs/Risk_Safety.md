# Risk & Safety Specification – LFP Age Classification System

## 1. Risk Register

| ID | Risk Description | Category | Likelihood | Impact | Risk Level | Mitigation | Control Metric |
|----|------------------|----------|------------|--------|------------|------------|----------------|
| R-01 | **PII leakage via logs** – Raw subject identifiers, device IDs, or health status logged without redaction | Privacy | Medium | High | High | Apply Presidio redaction at log boundary; enforce logging policy in CI; gitleaks scan | Number of PII log lines = 0 (CI failure) |
| R-02 | **Unauthorized tool call** – An attacker crafts an input that triggers tool `delete_patient_data` without proper role | Security | Low | Critical | High | Tool allowlist with RBAC; parameter validation; confirmation gate for write operations | `make test-safety` must pass (all tool-blocking tests) |
| R-03 | **Model regression under adversarial input** – A crafted input causes the model to output unsafe prediction (e.g., age outside valid range) | Safety | Medium | Medium | Medium | Red-team test suite in CI; output schema validation; confidence threshold (0.6) | `make test-safety` must pass (format/refusal tests) |
| R-04 | **Data drift causing silent degradation** – Input distribution shifts (e.g., new recording hardware) – accuracy drops without immediate detection | Quality | High | Medium | High | Drift monitoring (PSI on signal distribution); weekly golden set evaluation; retrain trigger | PSI < 0.1 (alert if exceeded) |
| R-05 | **Secrets in code** – API keys, database passwords committed to repository | Security | Medium | Critical | High | gitleaks in CI as hard gate; secrets management via GitHub Secrets | gitleaks scan must pass (no secrets leaked) |
| R-06 | **Overblocking legitimate requests** – Too strict validation blocks correct inputs | UX | Medium | Low | Low | Monitor refusal rate; tune thresholds with data; allowlist exceptions on case-by-case basis | Refusal rate < 5% of total requests |
| R-07 | **High-cost inference due to model complexity** – Larger model exceeds cost budget | Cost | Low | Medium | Medium | Cost per request monitoring; enforce budget alarm; fallback to cheaper model | Daily cost < budget (alert if >80%) |

## 2. Control Metrics

| Control | Implementation | Verification |
|---------|---------------|--------------|
| Tool allowlist | `configs/tool_allowlist.yaml` with schema, permission level, confirmation gate | `make test-safety` (tool-blocking tests) |
| Input schema validation | `src/tool_validator.py` using JSON Schema | `make test-safety` (schema tests) |
| PII redaction | Presidio middleware in preprocessing pipeline | Visual review + gitleaks scan |
| Secret scanning | gitleaks GitHub Action (hard fail) | CI step |
| Red-team testing | `tests/redteam/` adversarial inputs, pytest harness | `make test-safety` (30+ inputs) |
| Drift monitoring | PSI calculation on signal distribution (weekly) | Alert if > 0.1 |
| Output validation | Output schema check (age 0–47, confidence [0,1]) | `make eval-gate` + `make slo-gate` |

## 3. Incident Response (Summary)

| Incident Type | Playbook | Owner |
|---------------|----------|-------|
| Data exposure | See Incident Type 4 in `docs/incident_playbook.md` | Security Engineer |
| Tool misuse | See Incident Type 5 | ML Engineer |
| Model safety regression | See Incident Type 6 | ML Engineer |
| Infrastructure / latency | See Incident Type 3 | MLOps Engineer |

## 4. Review Cycle

- Risk register reviewed quarterly.
- Red-team inputs updated when new failure modes are discovered.
- Tool allowlist changed only via PR with approval (CODEOWNERS).