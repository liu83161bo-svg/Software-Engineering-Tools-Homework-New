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