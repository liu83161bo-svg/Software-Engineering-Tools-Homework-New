#!/usr/bin/env python3
"""
Real SLO Gate: loads model, measures inference latency & accuracy on golden set.
Fails if latency > SLO or accuracy < threshold.
"""
import pandas as pd
import numpy as np
import pickle
import time
import sys
import os

GOLDEN_PATH = "data/golden_set.csv"
MODEL_PATH = "models/eval_model.pkl"
LATENCY_SLO_MS = 30
ACCURACY_THRESHOLD = 0.85

def main():
    if not os.path.exists(GOLDEN_PATH):
        print(f"[FAIL] Golden set not found at {GOLDEN_PATH}")
        sys.exit(1)
    if not os.path.exists(MODEL_PATH):
        print(f"[FAIL] Model not found at {MODEL_PATH}")
        sys.exit(1)

    df = pd.read_csv(GOLDEN_PATH)
    #  golden set （30）
    X = df.iloc[:, 2:].values
    y_true = df.iloc[:, 1].values

    with open(MODEL_PATH, "rb") as f:
        model = pickle.load(f)

    # p95
    latencies = []
    for i in range(len(X)):
        start = time.perf_counter()
        _ = model.predict(X[i:i+1])
        elapsed = time.perf_counter() - start
        latencies.append(elapsed * 1000)  # 转为 ms
    p95_latency = np.percentile(latencies, 95)

    y_pred = model.predict(X)
    accuracy = np.mean(y_true == y_pred)

    print("SLO Gate Results:")
    print(f"  Number of samples: {len(X)}")
    print(f"  p95 latency: {p95_latency:.2f} ms (SLO <= {LATENCY_SLO_MS} ms)")
    print(f"  Accuracy: {accuracy:.4f} (threshold >= {ACCURACY_THRESHOLD})")

    failures = []
    if p95_latency > LATENCY_SLO_MS:
        failures.append(f"Latency SLO breached: {p95_latency:.2f} ms > {LATENCY_SLO_MS} ms")
    if accuracy < ACCURACY_THRESHOLD:
        failures.append(f"Accuracy below threshold: {accuracy:.4f} < {ACCURACY_THRESHOLD}")

    if failures:
        print("\nSLO Gate FAILED:")
        for f in failures:
            print(f"  - {f}")
        sys.exit(1)
    else:
        print("\nSLO Gate passed.")
        sys.exit(0)

if __name__ == "__main__":
    main()