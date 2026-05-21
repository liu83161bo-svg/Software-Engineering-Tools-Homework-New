# LFP Age Classification

A deep learning project for age classification from local field potential (LFP) signals.<br>The pipeline includes training, testing, Grad‑CAM interpretability, ablation studies, parameter sweep, developmental profile analysis, and more.

## Project Structure

```text
├── config/
│   └── default_config.py       # All hyperparameters and settings
├── data_process/
│   ├── __init__.py
│   ├── filters.py              # Bandpass and highpass filter functions
│   ├── processing.py           # Normalization, label encoding, LFPDataset
│   ├── loader.py               # Data loading from .mat or CSV
│   └── raw_reader.py           # Read raw signal from HDF5
├── models/
│   ├── __init__.py
│   ├── attention.py            # AttnPool1d module
│   └── classifier.py           # AgeClassifier (CNN + attention)
├── training/
│   ├── __init__.py
│   ├── main_train.py           # Training entry point
│   ├── trainer.py              # Training loop with early stopping
│   └── export.py               # Save test sample info to CSV
├── interpretation/
│   ├── __init__.py
│   ├── gradcam.py              # Grad‑CAM 1D generation with multi‑region detection
│   └── utils/
│       ├── __init__.py
│       ├── adaptive_threshold.py   # Adaptive threshold computation
│       └── statistical.py          # Statistical region detection
├── analysis/
│   ├── __init__.py
│   ├── confusion_matrix.py     # Overall confusion matrix
│   ├── save_results.py         # Save per‑age test results to CSV
│   ├── summary_plots.py        # Age‑wise CAM summary (4×4 grid)
│   ├── parameter_sweep.py      # Sweep window size / threshold
│   ├── single_signal_analysis.py  # Single signal ablation + threshold plot
│   ├── filter_sweep_analysis.py   # Bandpass filter sweep (paper figures)
│   ├── developmental_profile.py   # Optimal filter per age
│   ├── cam_duration_accuracy.py   # Duration/chunk accuracy analysis
│   ├── average_cam_analysis.py     # Per‑age CAM zeroing & visualization (average CAM)
│   └── main_analysis.py            # Unified analysis entry point
├── scripts/                     # Standalone utility scripts (see below)
│   ├── check_training_status.sh      # Check training progress
│   ├── train.sh                                   # Train with specified GPU
│   ├── view_training_log.sh		# View real‑time logs
│   ├── data_quality_report.py           # Data anomaly inspection & distribution plot
│   ├── filter_param_search.py           # Grid search for optimal filter parameters
│   └── visualize_filter_effects.py      # Compare filter effect on a single signal
├── utils/
│   ├── __init__.py
│   ├── environment.py          # Package and CUDA check
│   └── logger.py               # Console & file logger
├── visualization/
│   ├── __init__.py
│   └── learning_curves.py      # Training loss/accuracy curves
└── README.md

```

## Quick Start

### 1\. Install dependencies

```bash
pip install -r requirements.txt
or
pip install torch pandas numpy scipy h5py scikit-learn matplotlib
```

### 2\. Prepare data

Place your `.mat` files (containing `lfpN` and optionally `par/Age`) in `./data/1000/`.<br>If you have a CSV file for filtering files, set `FILTER_CSV` in `config/default_config.py`.

### 3\. Training

```bash
python training/main_train.py
```

The best model is saved to the path specified by `MODEL_SAVE_PATH` in the config.

Training-related parameters are defined in config/default\_config.py

### 4\. Analysis

Edit `config/default_config.py` to enable the desired analysis mode:

| Setting | Description |
| --- | --- |
| `TEST_SINGLE_SIGNAL = True` | Run ablation + threshold plot for one signal |
| `GENERATE_PAPER_FIGURES = True` | Add bandpass sweep figures (only with single signal) |
| `USE_PARAMETER_SWEEP = True` | Sweep threshold parameters |
| `GENERATE_DEVELOPMENTAL_PROFILE = True` | Find optimal bandpass per age |
| `GENERATE_CAM_DURATION_ACCURACY = True` | Duration/chunk accuracy analysis |
| `USE_BATCH_TESTING = True` | **Batch mode:** run independent multi-region detection & ablation on **each signal**, then compute summary statistics and generate individual results JSON + CSV/figures. Much slower but avoids “average CAM” bias. |
| *(All `False`)* | Run the default per‑age CAM zeroing pipeline (uses average CAM per age) |

Then run:

```bash
python main_analysis.py
```

## Configuration

All important settings are located in `config/default_config.py`. Key groups:

-   **Filter parameters** – `USE_FILTER`, `FILTER_TYPE`, `LOW_CUTOFF`, `HIGH_CUTOFF`, etc.
    
-   **Training parameters** – `NUM_EPOCHS`, `BATCH_SIZE`, `LEARNING_RATE`, `MODEL_SAVE_PATH`.
    
-   **Adaptive threshold** – `USE_ADAPTIVE_THRESHOLD`, `ADAPTIVE_METHOD`, `WINDOW_SIZE`, etc.
    
-   **Statistical detection** – `USE_STATISTICAL_DETECTION`, `METHOD`, `PERCENTILE`.
    
-   **Analysis output** – `CREATE_OUTPUT_DIR`, `OUTPUT_DIR_PREFIX`.
    

## Notes

-   All signals are normalized to zero mean and unit variance **once** during loading (in `loader.py`).
    
-   The model uses an attention‑pooling layer (`AttnPool1d`) instead of global average pooling.
    
-   Grad‑CAM is computed on the last convolutional layer of the feature extractor.
    
-   Reproducibility can be enabled via `USE_REPRODUCIBLE` and `RANDOM_SEED`.
    

## License

This project is for research purposes only.