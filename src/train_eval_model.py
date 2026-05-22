#!/usr/bin/env python3
"""Train a compact Random Forest model for eval gate."""
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import pickle
import os
import sys

DATA_PATH = "../data/training_data.csv"
MODEL_PATH = "../models/eval_model.pkl"
RANDOM_STATE = 42


def main():
    if not os.path.exists(DATA_PATH):
        print(f"[ERROR] Training data not found at {DATA_PATH}")
        sys.exit(1)

    print(f"[INFO] Loading data from {DATA_PATH} ...")
    df = pd.read_csv(DATA_PATH)
    X = df.iloc[:, 2:].values  # 1000 signal points
    y = df["age"].values
    print(f"       X: {X.shape}, y: {y.shape}")

    X_train, X_val, y_train, y_val = train_test_split(
        X, y, test_size=0.2, random_state=RANDOM_STATE, stratify=y
    )
    print(f"       Train: {X_train.shape[0]}, Val: {X_val.shape[0]}")

    # Compact RF: 50 trees, max_depth=20, no bootstrap to reduce redundancy
    print("[INFO] Training compact Random Forest ...")
    clf = RandomForestClassifier(
        n_estimators=50,
        max_depth=20,
        min_samples_leaf=5,
        random_state=RANDOM_STATE,
        n_jobs=-1,
        verbose=1
    )
    clf.fit(X_train, y_train)

    val_acc = accuracy_score(y_val, clf.predict(X_val))
    print(f"       Validation accuracy: {val_acc:.4f}")

    # Save model with highest compression
    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    with open(MODEL_PATH, "wb") as f:
        pickle.dump(clf, f, protocol=pickle.HIGHEST_PROTOCOL)

    # Print model size
    model_size = os.path.getsize(MODEL_PATH) / (1024 * 1024)
    print(f"[INFO] Model saved to {MODEL_PATH} ({model_size:.2f} MB)")


if __name__ == "__main__":
    main()