#!/usr/bin/env python3
"""Compute case-level metrics for binary security predictions."""

import argparse
import json
from pathlib import Path

import pandas as pd

METHODS = ("checkov_detected", "llm_detected")
VALID_PREDICTIONS = {"", "0", "1", "NA"}


def score(y_true, y_pred):
    tp = sum(t == 1 and p == 1 for t, p in zip(y_true, y_pred))
    fp = sum(t == 0 and p == 1 for t, p in zip(y_true, y_pred))
    fn = sum(t == 1 and p == 0 for t, p in zip(y_true, y_pred))
    tn = sum(t == 0 and p == 0 for t, p in zip(y_true, y_pred))

    precision = tp / (tp + fp) if tp + fp else None
    recall = tp / (tp + fn) if tp + fn else None

    f1 = (
        2 * precision * recall / (precision + recall)
        if precision is not None
        and recall is not None
        and precision + recall
        else None
    )

    return {
        "n_scored": len(y_true),
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "tn": tn,
        "precision": precision,
        "recall": recall,
        "f1": f1,
    }


def validate_inputs(labels, preds):
    required_labels = {"case_id", "vulnerable"}
    required_preds = {"case_id", *METHODS}

    if not required_labels.issubset(labels.columns):
        raise ValueError(
            f"Labels must contain columns: {sorted(required_labels)}"
        )

    if not required_preds.issubset(preds.columns):
        raise ValueError(
            f"Predictions must contain columns: {sorted(required_preds)}"
        )

    for name, frame in (("labels", labels), ("predictions", preds)):
        if frame["case_id"].isna().any() or (
            frame["case_id"].str.strip() == ""
        ).any():
            raise ValueError(f"{name} contains an empty case_id")

        if frame["case_id"].duplicated().any():
            raise ValueError(f"{name} contains duplicate case_id values")

    label_ids = set(labels["case_id"])
    prediction_ids = set(preds["case_id"])

    missing = label_ids - prediction_ids
    unexpected = prediction_ids - label_ids

    if missing or unexpected:
        raise ValueError(
            f"Case ID mismatch: missing predictions={sorted(missing)}, "
            f"unexpected predictions={sorted(unexpected)}"
        )

    valid_labels = labels["vulnerable"].astype(str).str.strip()
    if not valid_labels.isin({"0", "1"}).all():
        raise ValueError("vulnerable must contain only 0 or 1")

    for method in METHODS:
        values = preds[method].astype(str).str.strip().str.upper()
        invalid = set(values) - VALID_PREDICTIONS
        if invalid:
            raise ValueError(
                f"{method} contains invalid values: {sorted(invalid)}"
            )


def evaluate(labels, preds):
    validate_inputs(labels, preds)

    merged = labels.merge(
        preds, on="case_id", validate="one_to_one"
    )

    report = {
        "warning": (
            "Pilot dataset only; interpret metrics cautiously."
        ),
        "n_labeled": len(labels),
        "methods": {},
    }

    for method in METHODS:
        values = merged[method].astype(str).str.strip().str.upper()
        scored = values.isin({"0", "1"})

        y_true = merged.loc[scored, "vulnerable"].astype(int).tolist()
        y_pred = values.loc[scored].astype(int).tolist()

        metrics = score(y_true, y_pred)
        metrics["n_excluded"] = int((~scored).sum())
        report["methods"][method] = metrics

    return report


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--labels", default="dataset/labels.csv")
    parser.add_argument("--predictions", default="results/predictions.csv")
    parser.add_argument("--out", default="results/metrics.json")
    args = parser.parse_args()

    labels = pd.read_csv(args.labels, dtype=str, keep_default_na=False)
    preds = pd.read_csv(
        args.predictions, dtype=str, keep_default_na=False
    )

    report = evaluate(labels, preds)

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2) + "\n")

    print(json.dumps(report, indent=2))
    print(f"\nWrote {out}")


if __name__ == "__main__":
    main()
