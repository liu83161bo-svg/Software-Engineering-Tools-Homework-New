#!/usr/bin/env python3
"""
Generate LFP signals with moderate distinguishability for age classification.
Adjustable parameters to control difficulty.
Output: ../data/training_data.csv (20000 samples)
"""

import numpy as np
import pandas as pd
import os
from numpy.random import default_rng

N_SAMPLES = 2000
N_SIGNAL_POINTS = 1000
SAMPLING_RATE = 1000
SEED = 42
AGE_VALUES = [0,1,2,3,4,5,6,7,10,11,12,13,16,19,26,47]

rng = default_rng(seed=SEED)
t = np.arange(N_SIGNAL_POINTS) / SAMPLING_RATE

def generate_signal(age: int, snr_db: float) -> np.ndarray:
    # Narrower frequency range: age 0 -> 8 Hz, age 47 -> 5 Hz
    freq = 8.0 - (age / 47.0) * 3.0  # 8 to 5 Hz
    # Random phase for each signal to make class overlap
    phase = rng.uniform(0, 2*np.pi)
    amplitude = 10.0 + (age / 47.0) * 20.0  # 10 to 30 uV
    signal = amplitude * np.sin(2 * np.pi * freq * t + phase)

    # Add jitter: random small frequency variation per point
    freq_jitter = rng.normal(0, 0.5, size=N_SIGNAL_POINTS)
    signal *= (1 + 0.1 * np.sin(2 * np.pi * (freq + freq_jitter) * t))

    # Add noise at lower SNR
    signal_power = np.var(signal)
    noise_power = signal_power / (10**(snr_db/10))
    noise = np.sqrt(noise_power) * rng.normal(size=N_SIGNAL_POINTS)
    signal += noise
    signal -= np.mean(signal)
    return signal

def main():
    os.makedirs("../data", exist_ok=True)
    rows = []
    for i in range(N_SAMPLES):
        age = rng.choice(AGE_VALUES)
        snr = rng.uniform(10, 20)  # lower SNR
        sig = generate_signal(age, snr)
        row = {"trial_id": i, "age": age}
        for j in range(N_SIGNAL_POINTS):
            row[f"s_{j}"] = sig[j]
        rows.append(row)
    df = pd.DataFrame(rows)
    df.to_csv("../data/training_data.csv", index=False)
    print(f"Generated {N_SAMPLES} modified trials (harder classification).")

if __name__ == "__main__":
    main()