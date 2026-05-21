# Acceptance Criteria Table – LFP Age Classifier

All thresholds are justified by research cost: a 2% accuracy drop means ~20 more misclassifications per 1000 subjects, wasting ~$200 in manual verification. Warnings appear at half the hard-block cost.

| ID | Category | Scenario Description | Metric | Hard Block Threshold | Warning Zone | Measurement Method | Action on Fail |
|----|----------|----------------------|--------|----------------------|--------------|--------------------|----------------|
| AC-01 | Normal | Clean EEG, clear age features | Accuracy on full test set | >= 0.85 | 0.82 <= acc < 0.85 | Stratified 15% hold-out; fixed seed 42 | Block release; retrain with extended epochs / data augmentation |
| AC-02 | Normal | Batch inference (64 trials) | Throughput (samples/s) | >= 100 | 80 <= thpt < 100 | Time 10 batches, average | Optimize data loading (multi-threading, pre-fetch) |
| AC-03 | Normal | Single trial inference | p95 latency (ms) | <= 100 ms | 80 < p95 <= 100 ms | time.perf_counter() on 100 trials | Simplify model (fewer channels, smaller CNN) or use TensorRT |
| AC-04 | Edge | Age near class boundary (e.g., age 12 vs 13) | Boundary accuracy (within +/-2 years) | >= 0.70 | 0.65 <= acc < 0.70 | Subset of test samples where true age diff <= 2 years | Augment training with synthetic boundary samples |
| AC-05 | Edge | Signal amplitude near saturation (+/-180 uV) | Prediction stability (CV of 10 runs) | CV <= 15% | 10% < CV <= 15% | Add small Gaussian noise (sigma=5 uV) to same sample 10 times | Improve normalization (robust scaling, clip outliers) |
| AC-06 | Edge | Slight length variation (950-1050 points) | Processing success rate | >= 95% of trials pass | 90% <= rate < 95% | Feed 100 artificially trimmed/padded trials | Fix truncation logic; log every failure |
| AC-07 | Negative | Input is not a .mat file (e.g. .txt) | Error detection rate | 100% (must reject) | N/A | Provide .txt / .csv / .jpg files | Return specific error code ERR_UNSUPPORTED_FORMAT |
| AC-08 | Negative | Missing required field (lfpN or par/Age) | Graceful handling | 100% (must return error, not crash) | N/A | Remove field from test .mat file | Return error code ERR_MISSING_FIELD with field name |
| AC-09 | Negative | High noise (add Gaussian sigma=50 uV) | Accuracy drop from clean baseline | Drop < 25 percentage points | 20% <= drop < 25% | Compare accuracy on clean vs noisy test set | Enhance denoising preprocessing; add noise augmentation during training |
| AC-10 | Negative | Oversized file (>1 GB) | Memory safety | No crash, graceful exit | N/A | Create synthetic .mat > 1 GB | Implement chunked loading; abort with user message |
| AC-11 | Statistical | Class imbalance (minority classes have few samples) | F1-score on minority classes | >= 0.75 | 0.70 <= f1 < 0.75 | Stratified evaluation; report per-class F1 | Use class-weighted loss; oversample minority |
| AC-12 | Statistical | Leave-one-subject-out cross-validation | Average accuracy across folds | >= 0.80 | 0.75 <= acc < 0.80 | Compute per-subject accuracy, average | Add subject-level augmentation; regularize more |
| AC-13 | Statistical | Multiple runs with same seed (seed=42) | Output consistency | 100% identical predictions | N/A | Run full pipeline 3 times, compare predictions | Fix all randomness sources (numpy, torch, DataLoader seeding) |
| AC-14 | System | Training interrupted mid-epoch | Recovery success (continue without loss) | >= 95% of training progress restored | 90% <= rate < 95% | Kill process after epoch 50, resume from checkpoint | Save checkpoint every 10 epochs; verify load consistency |
| AC-15 | System | New age class added (e.g., age 48) | Old class performance drop | Drop < 5% on all old classes | 3% <= drop < 5% | Fine-tune with frozen feature extractor; measure old class accuracy | Expand output layer; use elastic architecture (e.g., additive expert) |
| AC-16 | System | Resource usage monitoring during training | Monitoring coverage | 100% of key metrics logged (GPU mem, CPU, time) | N/A | Check logs for interval < 5s per metric | Implement Prometheus / custom logger |

**Measurement Notes**:
- All offline eval uses the same golden test set (versioned in data/golden/).
- Online (inference) metrics are simulated in a staging environment before deployment.
- CI pipeline must pass all 16 criteria before a model version is promoted to production.

**Failure Handling Protocol**:
Test Failure -> Log details (ID, actual value, expected) -> Classify (performance / functional / data / system) -> Corrective action -> Retest in CI