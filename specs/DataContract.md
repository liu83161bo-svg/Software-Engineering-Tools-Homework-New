# Data Contract – LFP Age Classification

## 1. Schema Contract

| Field | Type | Constraints | Severity |
| trial_id | int64 | Unique | Critical |
| file_name | string | Must end with .mat | Critical |
| trial_index | int64 | >= 0 | Critical |
| age | int64 | 0 <= age <= 47 | Critical |
| signal | float32[1000] | -500 <= value <= 500 | High |
| quality_flag | int64 | 0,1,2 only | High |

## 2. Quality Contract

### Syntactic Rules (SYN)
| ID | Rule | Severity | Action |
| SYN-01 | File must be valid .mat (HDF5) | Critical | Reject file |
| SYN-02 | Required fields (lfpN, Age) present | Critical | Reject file |
| SYN-03 | No NaN / Inf in signal | High | Mark as poor quality |

### Structural Rules (STR)
| ID | Rule | Severity | Action |
| STR-01 | Signal length exactly 1000 | Critical | Reject trial |
| STR-02 | No duplicate trial_id | Medium | Auto-correct |
| STR-03 | Subject-level split – no same subject in train+test | Critical | Re-partition |
| STR-04 | Age consistent within subject | High | Use majority age |

### Statistical Rules (STA)
| ID | Rule | Threshold | Action |
| STA-01 | Signal mean within range | -200 <= mu <= 200 uV | Mark as outlier |
| STA-02 | Age distribution: no single class > 25% | Max 25% | Apply re-weighting |
| STA-03 | Minimum SNR >= 20 dB | >= 20 dB | Filter/reject |
| STA-04 | Source dominance: no single file > 20% of total | <= 20% | Alert if exceeded |

## 3. Validation Gates

- Data Gate: Run all SYN + STR checks on each new dataset version.
- Staging Gate: Run STA checks after data pipeline.
- Release Gate: All checks must pass; if any Critical fails, block release.

## 4. Breach Handling

| Level | Definition | Response Time |
| Level 1 | Critical breach (data corruption, privacy) | Immediate |
| Level 2 | Major breach (SLA missed >10%) | 4 hours |
| Level 3 | Minor breach (quality target missed) | 24 hours |
| Level 4 | Informational (performance degradation) | 3 days |

Remediation Process: Detection -> Classification -> Containment -> Investigation -> Correction -> Validation -> Communication.