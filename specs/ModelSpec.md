# Model Specification - EEG Age Classifier

## 1. Baseline Model
### 1.1 Current Baseline (Production)
- **Model**: CNN with Attention Pooling (AgeClassifier)
- **Architecture**: 
  - 4 convolutional layers (64-128-256-512 channels)
  - Attention pooling over time dimension
  - 3 fully connected layers (512-256-128)
- **Input**: 1000Hz EEG signal, 1000 time points
- **Output**: Age classification (16 age categories)
- **Performance**: ~85% accuracy on validation set

### 1.2 Simple Baselines (For Comparison)
- **Rule-based baseline**: Majority class prediction
- **Statistical baseline**: Linear regression on signal features
- **Simple ML baseline**: Random Forest with extracted features

## 2. Eval Gate Model (Random Forest)
A lightweight model specifically trained for the evaluation gate (golden set testing).
This model is **not** intended for production deployment; its sole purpose is to provide
a real, reproducible inference pipeline for the CI evaluation gate.

- **Type**: Random Forest Classifier, 200 trees
- **Input**: 1000 LFP signal points (preprocessed, zero-mean)
- **Output**: 16 age classes (0–47)
- **Training data**: 20,000 simulated LFP trials (ages 0–47, SNR 10–20 dB)
- **Validation accuracy**: 97.6%
- **Artifact**: `models/eval_model.pkl`
- **Reproducible**: fixed seed 42, training script `src/train_eval_model.py`

## 3. Applicability Limits
### 3.1 Domain Constraints (applies to both models)
- **Input signal**: Must be 1000Hz EEG, bandpass filtered (8-100Hz)
- **Signal length**: Exactly 1000 time points
- **Age range**: 0-47 years (16 discrete categories)
- **Data source**: Compatible with .mat format from specified recording setup

### 3.2 Out-of-Distribution Detection
- Signals with SNR < 10dB should be flagged
- Age predictions beyond 0-100 years considered invalid
- Unusual signal patterns (epileptic spikes) should trigger fallback

## 4. Resource Envelope
### 4.1 CNN Baseline Model
- **Training**: ~30 minutes on GPU
- **Inference**: <10ms per sample on CPU
- **Memory**: Model size ~15MB

### 4.2 Eval Gate Model (Random Forest)
- **Training**: ~5 minutes on CPU (20,000 samples, 200 trees)
- **Inference**: <5ms per sample on CPU
- **Memory**: Model size ~300 MB (pickle) – acceptable for CI, not for production

## 5. Update Policy
### 5.1 Baseline Model Updates
- **Performance degradation**: >5% accuracy drop on golden set
- **Data drift**: Statistical shift in input distribution
- **New age categories**: Adding age groups outside current range
- **Hardware changes**: Migration to new inference hardware

### 5.2 Eval Gate Model Updates
- Retrained each time the baseline model changes, using the same training script
- Update policy: always keep eval gate model in sync with the baseline’s data distribution

## 6. Failure Modes & Fallbacks
### 6.1 Detected Failures
- High prediction uncertainty (>0.8 entropy)
- Out-of-distribution signals
- Hardware failure (GPU unavailable)

### 6.2 Fallback Strategies
1. **Primary**: Return to previous model version
2. **Secondary**: Rule-based age estimation
3. **Tertiary**: Flag for human review