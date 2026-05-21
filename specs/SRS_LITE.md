# Software Requirements Specification (Lite) – LFP Age Classifier

## 1. Input / Output Schema

### Input
* Format: .mat (MATLAB v7.3 / HDF5)
* Required fields:
  - lfpN: float32 array, shape [n_trials, 1000], unit uV, sampled at 1000 Hz.
  - par/Age: scalar integer in {0,1,2,3,4,5,6,7,10,11,12,13,16,19,26,47} (16 discrete ages).
* Optional fields: channel_names, other par/* metadata.

### Output
* Training phase:
  - model checkpoint: .pth (PyTorch)
  - training logs: metrics + visualization
* Inference phase (single trial):
  - predicted_class: int [0-15]
  - age_label: int (corresponding to original age)
  - confidence: float [0.0, 1.0]
  - optional: class_probabilities, attention_weights

## 2. Degradation Rules

| Condition | Threshold | Action |
|-----------|-----------|--------|
| Single inference timeout | > 500 ms | Log warning; return fallback_used=true with most frequent class |
| Batch inference (64 trials) timeout | > 5 s | Abort batch; fallback to per-trial inference |
| Low confidence | max probability < 0.6 | Flag output as low_confidence; route to human review |
| Poor signal quality | amplitude > +/-200 uV or SNR < 15 dB | Reject trial; log error; do not use for training |
| Missing required field | lfpN or par/Age absent | Return specific error code (e.g., ERR_MISSING_FIELD) |
| Model loading failure | .pth corrupt or version mismatch | Load fallback baseline model (logistic regression on band power) |

## 3. Non-Functional Requirements (NFRs)

| NFR | Target | Measurement Method | Justification |
|-----|--------|--------------------|---------------|
| Test accuracy | >= 85% | Stratified 15% hold-out test set; fixed seed | Current best model achieves 87%; 85% is minimum acceptable for publication |
| Inference latency (p95) | <= 100 ms per trial | time.perf_counter() averaged over 100 runs on RTX 3090 | Enables real-time feedback in research setting |
| Training time | <= 2 h for 200 epochs | End-to-end timing on a single RTX 3090 | Allows multiple experiments per workday |
| GPU memory | < 8 GB peak | nvidia-smi monitoring | Compatible with common GPUs (RTX 2080, 3090) |
| Model size | < 100 MB | File size of .pth | Easy to share and version-control |
| Reproducibility | 100% identical results with fixed seed (42) | Run twice with same seed, compare predictions | Required for scientific validity |
| Storage cost | < 10 GB for all data + models | Periodic cleanup | Avoids disk overflow on shared cluster |

## 4. Acceptance Checklist (High-Level)

- [ ] All acceptance criteria in Acceptance_Criteria_Table.md pass.
- [ ] Offline eval gate: accuracy >= 85% on golden test set.
- [ ] Data gate: input files pass schema validation (required fields present, data type correct).
- [ ] Degradation tests: fallback works under timeout / missing fields.
- [ ] Reproducibility: two runs with same seed yield identical predictions.