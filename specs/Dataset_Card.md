# Dataset Card – LFP Age Classification

## 1. Dataset Description

- Name: LFP Age Classification Dataset v1.0.0
- Modality: Local field potential (single-channel, 1000 Hz)
- Size: ~50,000 trials, ~5 GB
- Format: .mat (HDF5)

## 2. Intended Use

- Research on brain age prediction from LFP signals.
- Model development and benchmarking.
- Not for clinical diagnostics or individual identification.

## 3. Non-Use Cases

- Clinical diagnostics (not validated).
- Employment / insurance decisions.
- Age extrapolation beyond 0-47.

## 4. Composition

| Split | Trials | Subjects |
| Train | ~35,000 | ~350 |
| Val   | ~7,500  | ~75  |
| Test  | ~7,500  | ~75  |

## 5. Labeling

- Age: self-report verified by researcher.
- Quality: expert review (SNR > 20 dB, no artifacts).
- Inter-rater agreement: 98%.

## 6. Known Limitations

- Ages >47 not represented.
- Single-channel (no spatial info).
- Controlled lab conditions; healthy subjects only.

## 7. Versions

| Version | Date | Changes |
| v1.0.0 | 2026-01-01 | Initial release |

## 8. Sample Dataset

This repository includes a simulated sample dataset: data/sample_lfp_data.csv (1000 rows). It contains 1000-point signals and associated metadata, enabling quick validation of the data pipeline without requiring the full dataset.