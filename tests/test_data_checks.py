"""Data quality checks for LFP Age Classification dataset.
Covers: 3 syntactic, 4 structural, 3 statistical = 10 checks.
Adapted for 1000-row sample dataset.
"""

import pandas as pd
import numpy as np
import os

SAMPLE_DATA_PATH = "data/sample_lfp_data.csv"


def load_sample_data():
    if not os.path.exists(SAMPLE_DATA_PATH):
        raise FileNotFoundError(f"Sample data not found at {SAMPLE_DATA_PATH}")
    return pd.read_csv(SAMPLE_DATA_PATH)


# ---------- Syntactic Checks (3) ----------
def test_syn_01_file_exists():
    assert os.path.exists(SAMPLE_DATA_PATH), f"File {SAMPLE_DATA_PATH} not found"
    df = pd.read_csv(SAMPLE_DATA_PATH)
    assert len(df) > 0, "File is empty"


def test_syn_02_required_columns_present():
    df = load_sample_data()
    required = ["trial_id", "file_name", "trial_index", "age", "quality_flag"]
    for col in required:
        assert col in df.columns, f"Missing required column: {col}"


def test_syn_03_no_null_values():
    df = load_sample_data()
    critical_cols = ["trial_id", "age", "file_name", "quality_flag"]
    assert df[critical_cols].isnull().sum().sum() == 0, "Null values found in critical columns"


# ---------- Structural Checks (4) ----------
def test_str_01_unique_trial_id():
    df = load_sample_data()
    assert df["trial_id"].is_unique, "Duplicate trial_id found"


def test_str_02_trial_index_non_negative():
    df = load_sample_data()
    assert (df["trial_index"] >= 0).all(), "Negative trial_index found"


def test_str_03_age_in_range():
    df = load_sample_data()
    assert df["age"].between(0, 47).all(), f"Age out of range: {df[~df['age'].between(0, 47)]}"


def test_str_04_file_name_pattern():
    df = load_sample_data()
    assert df["file_name"].str.endswith(".mat").all(), "Some file_names do not end with .mat"


# ---------- Statistical Checks (3) ----------
def test_sta_01_age_distribution_no_single_class_over_25_percent():
    df = load_sample_data()
    dist = df["age"].value_counts(normalize=True)
    max_prop = dist.max()
    assert max_prop <= 0.25, f"Age class {dist.idxmax()} represents {max_prop:.1%} of data (limit: 25%)"


def test_sta_02_quality_flag_distribution():
    df = load_sample_data()
    ratio_ok = (df["quality_flag"] >= 1).mean()
    assert ratio_ok >= 0.50, f"Only {ratio_ok:.1%} of rows have quality_flag >= 1 (min 50%)"


def test_sta_03_source_dominance():
    df = load_sample_data()
    source_counts = df["file_name"].value_counts(normalize=True)
    max_source = source_counts.max()
    assert max_source <= 0.20, f"File {source_counts.idxmax()} represents {max_source:.1%} of data (limit: 20%)"