#!/usr/bin/env python3
"""
Generate a simulated LFP dataset for age classification.
Output: data/sample_lfp_data.csv with 100 rows.
Each row contains:
  - file_name, trial_id, trial_index, age, quality_flag
  - 1000 signal columns: signal_0 .. signal_999
"""

import numpy as np
import pandas as pd
import os
from numpy.random import default_rng

# Parameters
N_TRIALS = 50
N_SIGNAL_POINTS = 1000
SAMPLING_RATE = 1000  # Hz
SEED = 42

# Age values (16 discrete ages from the real project)
AGE_VALUES = [0, 1, 2, 3, 4, 5, 6, 7, 10, 11, 12, 13, 16, 19, 26, 47]

# Output directory
OUTPUT_DIR = "../data"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "sample_lfp_data.csv")

rng = default_rng(seed=SEED)


def generate_signal(age: int, snr_db: float) -> np.ndarray:
    """Generate a synthetic LFP signal based on age."""
    freq = 15.0 - (age / 47.0) * 11.0  # 15 to 4 Hz
    amplitude = 10.0 + (age / 47.0) * 30.0  # 10 to 40 µV
    t = np.arange(N_SIGNAL_POINTS) / SAMPLING_RATE

    signal = (
        0.6 * amplitude * np.sin(2 * np.pi * freq * t + rng.uniform(0, 2*np.pi))
        + 0.3 * amplitude * np.sin(2 * np.pi * (freq / 2) * t + rng.uniform(0, 2*np.pi))
        + 0.1 * amplitude * np.sin(2 * np.pi * (freq * 2) * t + rng.uniform(0, 2*np.pi))
    )
    signal += 2.0 * np.sin(2 * np.pi * 0.5 * t + rng.uniform(0, 2*np.pi))

    # Add noise at given SNR
    signal_power = np.var(signal)
    noise_power = signal_power / (10 ** (snr_db / 10))
    noise = np.sqrt(noise_power) * rng.normal(size=N_SIGNAL_POINTS)

    return signal + noise


def generate_dataset():
    """Main generation function."""
    records = []
    trial_counter = 0

    # Generate 10 subjects, each with a *unique* age
    # shuffle AGE_VALUES and pick first 10
    unique_ages = rng.choice(AGE_VALUES, size=10, replace=False)  # <- 关键修改

    for subject_idx, age in enumerate(unique_ages):
        subject_id = subject_idx + 1
        n_trials_per_subject = N_TRIALS // 10  # 10 trials each
        for trial_in_subject in range(n_trials_per_subject):
            trial_counter += 1
            session = rng.integers(1, 4)
            condition = rng.choice(["rest", "task"])
            file_name = f"sub{subject_id:03d}_ses{session}_{condition}.mat"

            snr_db = rng.uniform(15, 35)
            signal = generate_signal(age, snr_db)

            if snr_db >= 25:
                quality_flag = 2
            elif snr_db >= 18:
                quality_flag = 1
            else:
                quality_flag = 0

            record = {
                "trial_id": trial_counter,
                "file_name": file_name,
                "trial_index": trial_in_subject,
                "age": age,
                "quality_flag": quality_flag,
            }
            for i in range(N_SIGNAL_POINTS):
                record[f"signal_{i}"] = signal[i]

            records.append(record)

    df = pd.DataFrame(records)
    df = df.sample(frac=1, random_state=SEED).reset_index(drop=True)
    return df


if __name__ == "__main__":
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print("Generating sample LFP dataset...")
    df = generate_dataset()
    df.to_csv(OUTPUT_FILE, index=False)
    print(f"Saved {len(df)} rows to {OUTPUT_FILE}")
    print("Unique ages assigned:", sorted(df["age"].unique()))