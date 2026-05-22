# Incident Playbook — LFP Age Classifier

## Incident Type 1: Data Incident (Schema Violation / Missing Features)
**Symptoms**: CI data check fails (`make data-check`), golden set shows null values, PSI > 0.1.

**Triage Steps**:
1. **Immediate** (within 5 min):
   - Pause any active canary; keep current model serving.
   - If production affected, consider rolling back to previous golden set version.
2. **Investigate** (within 30 min):
   - Identify which field(s) caused violation (run `scripts/check_data_quality.py`).
   - Verify if it's transient or permanent schema change.
3. **Resolution**:
   - If temporary: wait for fix from upstream, re-run `make data-check`.
   - If permanent: update `DataContract.md`, re-validate, retrain model.

**Rollback Procedure**:
- `make rollback` (restores previous model version; golden set is versioned in `data/golden_set.csv`).
- Re-run CI to verify; if passes, promote previous version.

**Postmortem**: Update data contract tests to catch this scenario; add alert for upstream changes.

---

## Incident Type 2: Model Incident (Quality Proxy Degradation)
**Symptoms**: `make eval-gate` fails (accuracy < 0.85 on golden set). Monitoring shows accuracy proxy drop.

**Triage Steps**:
1. **Immediate** (within 5 min):
   - If canary active, revert to 100% old model (reroute traffic).
   - If full production, `make rollback` to previous model.
   - Notify ML team.
2. **Investigate** (within 60 min):
   - Compare metrics between old and new model on golden set (`scripts/eval_gate.py`).
   - Evaluate per-age slice performance.
   - Check if evaluation data distribution differs from training (drift report).
3. **Resolution**:
   - If regression due to data shift: collect new samples, retrain.
   - If regression due to model change: revert, fix training pipeline.

**Rollback Procedure**:
- `make rollback` (copies `models/previous_model.pkl` to `models/eval_model.pkl`).
- Run `make eval-gate` and `make slo-gate` to verify.

**Postmortem**: Add slice-specific gate to CI; improve golden set coverage for degraded ages.

---

## Incident Type 3: Infrastructure Incident (Latency SLO Breach)
**Symptoms**: `make slo-gate` fails (p95 latency > 30ms), monitoring shows latency spike.

**Triage Steps**:
1. **Immediate** (within 2 min):
   - Check CPU/memory saturation via `top` or container metrics.
   - If scaling enabled, check auto-scaler logs; if not, manually scale up.
   - If latency persists, `make rollback` to previous stable model.
2. **Investigate** (within 30 min):
   - Profile inference code — is the model slower due to weight changes?
   - Check for memory leak or concurrent request spike.
3. **Resolution**:
   - If model is slower: optimize (quantization, ONNX) or use smaller architecture.
   - If infra issue: adjust autoscaling config, add caching.

**Rollback Procedure**:
- `make rollback` (restore previous model).
- Validate after rollback: `make slo-gate` passes.

**Postmortem**: Add latency gate to CI for each model version; introduce load testing in staging.

---

## Incident Type 4: Security Incident — Data Exposure (PII Leak)
**Symptoms**: Log monitoring detects raw PII (names, emails, or subject IDs) in log files; secret scanning alert fires; gitleaks reports hardcoded credentials.

**Triage Steps**:
1. **Immediate** (within 5 min):
   - Rotate any exposed API keys, database credentials, or secrets.
   - Isolate affected logs: prevent further ingestion; tag logs as potentially compromised.
   - Check retention window — can logs be purged? If still within retention, delete immediately.
2. **Investigate** (within 30 min):
   - Determine which dataset versions or model artifacts may contain PII.
   - Trace the source: was PII introduced at data collection, preprocessing, or logging pipeline?
3. **Containment**:
   - Apply Presidio redaction middleware at the log boundary to prevent future leaks.
   - Remove affected logs from monitoring systems; do not use contaminated data for training.
4. **Resolution**:
   - Patch the logging pipeline to redact PII before storage.
   - Increase secret scanning frequency; add gitleaks as a hard CI gate (already in place).

**Rollback Procedure**: Not directly applicable; instead, revert to a prior configuration of the logging pipeline that did not log raw payloads. Update `configs/logging_config.yaml` and redeploy.

**Postmortem**: Update privacy policy (`specs/SafetyPolicy.md`) to explicitly forbid raw PII logging; add automated alert for any log line containing patterns like `[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}`.

---

## Incident Type 5: Security Incident — Tool Misuse (Unauthorized Tool Call)
**Symptoms**: Monitoring shows calls to non-allowlisted tools (e.g., `delete_patient_data` from non-admin role); `make test-safety` fails with tool-blocking tests.

**Triage Steps**:
1. **Immediate** (within 2 min):
   - Identify source IP or user account – is it a compromised credential?
   - Check if any destructive operations were actually executed (e.g., data deletion, record modification).
2. **Containment**:
   - Revoke the compromised credentials; block the source IP at the API gateway if necessary.
   - Enable mandatory confirmation gate for all write operations (already in tool allowlist).
3. **Investigate** (within 30 min):
   - Review logs to understand the attack pattern: was it a brute force attempt, prompt injection, or compromised token?
   - Check if the attempt targeted specific tools or was random.
4. **Resolution**:
   - Update tool allowlist to restrict roles further; enforce RBAC at the application level.
   - Run full red-team test suite to verify no regression (`pytest tests/test_safety.py -v`).

**Rollback Procedure**: `make rollback` does not apply directly. Instead, revert to the previous version of `configs/tool_allowlist.yaml` if it was recently changed. Use `git checkout HEAD~1 -- configs/tool_allowlist.yaml` and redeploy.

**Postmortem**: Add more adversarial tool calls to red-team suite; implement rate limiting on tool endpoints.

---

## Incident Type 6: Security Incident — Model Safety Regression
**Symptoms**: `make test-safety` fails (a previously safe adversarial test now bypasses controls); a new prompt or model version produces unsafe output that was previously blocked.

**Triage Steps**:
1. **Immediate** (within 5 min):
   - Do not deploy the new model version; rollback to previous champion model if already in production.
   - Pause any ongoing canary or ramp-up; freeze releases.
2. **Investigate** (within 30 min):
   - Identify which safety test(s) failed: format compliance, refusal correctness, or tool blocking.
   - Check recent changes to the tool validator (`src/tool_validator.py`), allowlist, or pre/post-processing logic.
   - Determine if the regression is due to model weight changes, prompt update, or validation code change.
3. **Containment**:
   - If the regression is in the validation code, apply a hotfix to restore previous behavior.
   - If the regression is model-driven, revert to the previous model and retrain with additional safety constraints.
4. **Resolution**:
   - Fix the root cause, update red-team inputs to cover the new failure vector, and re-run full safety suite (`make test-safety`).
   - Commit the fix and re-approve release after all gates pass.

**Rollback Procedure**: `make rollback` (restore previous model + previous `src/tool_validator.py` if needed). Use git to revert the specific commit that introduced the regression.

**Postmortem**: Add the new failure case to the red-team regression suite; document the root cause and update the safety policy if needed.