#!/usr/bin/env python3
"""
Real evaluation gate – loads the trained RandomForest model,
predicts on golden set, checks thresholds.
"""
import pandas as pd
import numpy as np
import yaml
import pickle
import sys
import os
import json
from pathlib import Path
from sklearn.metrics import f1_score

GOLDEN_PATH = "../data/golden_set.csv"
MODEL_PATH = "../models/eval_model.pkl"
THRESHOLDS_PATH = "../configs/thresholds.yaml"
METRICS_HISTORY = "../reports/metrics_history.json"

def load_golden():
    df = pd.read_csv(GOLDEN_PATH)
    X = df.iloc[:, 2:].values  # skip trial_id, age
    y = df["age"].values
    return X, y

def load_model():
    with open(MODEL_PATH, "rb") as f:
        model = pickle.load(f)
    return model

def load_thresholds():
    with open(THRESHOLDS_PATH) as f:
        return yaml.safe_load(f)

def compute_metrics(y_true, y_pred):
    accuracy = np.mean(y_true == y_pred)
    macro_f1 = f1_score(y_true, y_pred, average='macro', zero_division=0)
    # slice accuracies
    def slice_acc(condition):
        idx = [i for i, t in enumerate(y_true) if condition(t)]
        if not idx:
            return None
        return float(np.mean(y_true[idx] == y_pred[idx]))
    slices = {
        "young_≤7": slice_acc(lambda x: x <= 7),
        "adolescent_10_13": slice_acc(lambda x: 10 <= x <= 13),
        "adult_≥16": slice_acc(lambda x: x >= 16),
    }
    return {"accuracy": float(accuracy), "macro_f1": float(macro_f1), "slices": slices}

def save_metrics(metrics):
    os.makedirs(Path(METRICS_HISTORY).parent, exist_ok=True)
    hist = []
    if os.path.exists(METRICS_HISTORY):
        with open(METRICS_HISTORY) as f:
            hist = json.load(f)
    hist.append(metrics)
    with open(METRICS_HISTORY, "w") as f:
        json.dump(hist, f, indent=2)

def check_gates(metrics, thresholds):
    gates = thresholds["gates"]
    failures = []
    acc_min = gates["hard"]["overall_accuracy"]["min"]
    if metrics["accuracy"] < acc_min:
        failures.append(f"Hard gate: accuracy {metrics['accuracy']:.3f} < {acc_min}")
    f1_min = gates["hard"]["macro_f1"]["min"]
    if metrics["macro_f1"] < f1_min:
        failures.append(f"Hard gate: macro_f1 {metrics['macro_f1']:.3f} < {f1_min}")
    for name, acc in metrics["slices"].items():
        if acc is not None:
            soft_min = gates["soft"]["per_slice_accuracy"]["min"]
            if acc < soft_min:
                print(f"  WARNING: slice '{name}' accuracy {acc:.3f} < {soft_min}")
    return failures

def main():
    print("=" * 50)
    print("Eval Gate: Loading golden set...")
    X, y_true = load_golden()
    print(f"  Loaded {len(X)} samples.")

    print("Loading model...")
    model = load_model()
    print(f"  Model type: {type(model).__name__}")

    print("Predicting...")
    y_pred = model.predict(X)
    thresholds = load_thresholds()
    metrics = compute_metrics(y_true, y_pred)

    print(f"  Accuracy:      {metrics['accuracy']:.4f}")
    print(f"  Macro F1:      {metrics['macro_f1']:.4f}")
    for s, v in metrics["slices"].items():
        print(f"  Slice '{s}': {v:.4f}" if v else f"  Slice '{s}': N/A")

    save_metrics(metrics)

    failures = check_gates(metrics, thresholds)
    if failures:
        print("\nGATE FAILED:")
        for f in failures:
            print(f"  - {f}")
        sys.exit(1)
    else:
        print("\nAll hard gates passed.")
        sys.exit(0)

if __name__ == "__main__":
    main()