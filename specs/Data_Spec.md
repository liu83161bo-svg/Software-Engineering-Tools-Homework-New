# Data Specification – LFP Age Classification

## 1. Sources & Rights

- Source: Local field potential (LFP) recordings from rodent experiments (single-channel, 1000 Hz sampling).
- Collection Entity: Neuroscience Laboratory, [Your Institution].
- Data Format: .mat (HDF5 v7.3) containing:
  - lfpN: float32 array, shape [n_trials, 1000], unit uV
  - par/Age: scalar integer (0,1,2,3,4,5,6,7,10,11,12,13,16,19,26,47)
- Usage Rights: Internal research only. Cannot be shared externally without ethical approval.
- Ethical Approval: IRB-2020-NEURO-015.

## 2. Data Versioning

| Version | Date | Changes |
| v1.0.0 | 2026-01-01 | Initial release |
| v1.1.0 (planned) | 2026-06-01 | Add multi-channel data |

Version naming: v<major>.<minor>.<patch>.

## 3. Schema & Semantics

### Input Schema
| Field | Type | Shape | Constraints | Description |
| trial_id | int64 | scalar | Unique | Auto-increment identifier |
| file_name | string | scalar | Must match *.mat | Source .mat filename |
| trial_index | int64 | scalar | >= 0 | Index within the file |
| age | int64 | scalar | 0 <= age <= 47 | Subject age at recording |
| signal | float32 | [1000] | -500 to +500 uV | Raw LFP time series |
| quality_flag | int64 | scalar | 0,1,2 | 0=poor, 1=acceptable, 2=good |

### Processing Pipeline
Raw .mat -> Quality Filtering -> Trial Extraction (1000 points) -> Normalization (z-score) -> Train/Val/Test Split (70/15/15 stratified by age)

## 4. Labeling Protocol

- Age Labels: Verified by researcher; all trials from same subject share the same age.
- Quality Labels: Manual expert review. Criteria: SNR > 20 dB, no saturation, no NaN.
- Inter-rater Agreement: 98% on quality labels (2 raters, 500-sample audit).

## 5. Coverage & Balance

| Age Group | Count | Percentage |
| 0-5 | 8,200 | 16.4% |
| 6-12 | 15,000 | 30.0% |
| 13-19 | 12,500 | 25.0% |
| 20-30 | 8,000 | 16.0% |
| 31-47 | 6,300 | 12.6% |

Splits: Subject-wise, stratified by age group. Fixed seed: 42.

## 6. Known Limitations

- Ages >47 not represented.
- Single-channel only (no spatial information).
- Controlled lab conditions (may not generalize to real-world).
- Healthy subjects only.