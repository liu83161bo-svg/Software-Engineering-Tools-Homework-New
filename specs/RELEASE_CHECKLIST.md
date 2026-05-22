# Release Checklist — LFP Age Classifier

## 1. Model Validation
- [ ] **Eval Gate Pass**: `make eval-gate` passes (accuracy ≥ 0.85 on golden set `data/golden_set.csv`).
- [ ] **SLO Gate Pass**: `make slo-gate` passes (p95 latency ≤ 30ms, accuracy ≥ 0.85).
- [ ] **Regression Check**: No metric drop > 5% compared to previous version (stored in `reports/metrics_history.json`).
- [ ] **Slice Performance**: per-age slice accuracy ≥ 0.75 for all slices; if any fails, document exception.

## 2. Data Validation
- [ ] **Data Contract Pass**: `make data-check` passes (syntactic, structural, statistical checks on golden set).
- [ ] **Golden Set Integrity**: Golden set `data/golden_set.csv` is versioned and matches expected distribution.
- [ ] **No Data Leakage**: Train/val/test split respects subject boundaries (confirmed by CI).

## 3. Infrastructure & Serving
- [ ] **Canary Test**: 5% traffic run for 30 minutes without SLO breach (see `docs/rollout_plan.md`).
- [ ] **Rollback Ready**: Previous model version (`models/previous_model.pkl`) exists and can be deployed within 5 minutes via `make rollback`.
- [ ] **Feature Flags**: All thresholds and flags are versioned in `configs/` and reviewed.

## 4. Security & Compliance
- [ ] **Secrets Management**: No hardcoded secrets in code or config; use GitHub Secrets.
- [ ] **Logging Policy**: No PII logged; logging level set to `INFO` in production.
- [ ] **Access Control**: Model artifact and golden set are readable only by authorized roles (via `.gitignore` and access control).

## 5. Documentation & Approval
- [ ] **Release Notes**: Describe what changed (model weights, thresholds, preprocessing) and why.
- [ ] **Incident Playbook**: Updated for current contacts and scenarios.
- [ ] **Owner Approval**: At least one team member (non-author) reviewed and signed off.

## 6. Observation Window After Release
- [ ] **Shadow Mode**: New model runs in shadow for 1 hour, outputs compared with production.
- [ ] **Gradual Ramp-Up**: 5% → 20% → 50% → 100% with 30-minute observation per step.
- [ ] **Kill Switch**: If any SLO is violated during ramp-up, revert immediately via `make rollback`.