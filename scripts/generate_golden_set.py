#!/usr/bin/env python3
"""
Generate a golden set (30 samples) for the LFP age classifier.
Using same signal model as training, but different random seed.
"""
import numpy as np
import pandas as pd
import os
from numpy.random import default_rng

N_GOLDEN = 30
N_SIGNAL_POINTS = 1000
SAMPLING_RATE = 1000
AGE_VALUES = [0,1,2,3,4,5,6,7,10,11,12,13,16,19,26,47]
SEED = 999  # Different from training seed (42)

rng = default_rng(seed=SEED)
t = np.arange(N_SIGNAL_POINTS) / SAMPLING_RATE

def generate_signal(age: int, snr_db: float) -> np.ndarray:
    freq = 8.0 - (age / 47.0) * 3.0
    phase = rng.uniform(0, 2*np.pi)
    amplitude = 10.0 + (age / 47.0) * 20.0
    signal = amplitude * np.sin(2 * np.pi * freq * t + phase)
    freq_jitter = rng.normal(0, 0.5, size=N_SIGNAL_POINTS)
    signal *= (1 + 0.1 * np.sin(2 * np.pi * (freq + freq_jitter) * t))
    signal_power = np.var(signal)
    noise_power = signal_power / (10**(snr_db/10))
    noise = np.sqrt(noise_power) * rng.normal(size=N_SIGNAL_POINTS)
    signal += noise
    signal -= np.mean(signal)
    return signal

def main():
    os.makedirs("../data", exist_ok=True)
    rows = []
    for i in range(N_GOLDEN):
        age = rng.choice(AGE_VALUES)
        snr = rng.uniform(10, 20)
        sig = generate_signal(age, snr)
        row = {"trial_id": i, "age": age}
        for j in range(N_SIGNAL_POINTS):
            row[f"s_{j}"] = sig[j]
        rows.append(row)
    df = pd.DataFrame(rows)
    df.to_csv("../data/golden_set.csv", index=False)
    print(f"Generated {N_GOLDEN} golden samples (seed={SEED}).")

if __name__ == "__main__":
    main()