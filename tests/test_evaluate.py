import pandas as pd
import pytest

from scripts.evaluate import evaluate, score


def make_labels():
    return pd.DataFrame({
        "case_id": ["TF001", "TF002", "TF003"],
        "vulnerable": ["1", "1", "0"],
    })


def make_predictions():
    return pd.DataFrame({
        "case_id": ["TF001", "TF002", "TF003"],
        "checkov_detected": ["1", "0", "0"],
        "llm_detected": ["1", "NA", "0"],
    })


def test_perfect_predictions():
    result = score([1, 0, 1, 0], [1, 0, 1, 0])

    assert result["tp"] == 2
    assert result["fp"] == 0
    assert result["fn"] == 0
    assert result["tn"] == 2
    assert result["precision"] == 1.0
    assert result["recall"] == 1.0
    assert result["f1"] == 1.0


def test_false_positive():
    result = score([0, 1], [1, 1])

    assert result["tp"] == 1
    assert result["fp"] == 1
    assert result["fn"] == 0
    assert result["tn"] == 0
    assert result["precision"] == 0.5
    assert result["recall"] == 1.0


def test_false_negative():
    result = score([1, 0], [0, 0])

    assert result["tp"] == 0
    assert result["fp"] == 0
    assert result["fn"] == 1
    assert result["tn"] == 1
    assert result["precision"] is None
    assert result["recall"] == 0.0


def test_empty_predictions():
    result = score([], [])

    assert result["n_scored"] == 0
    assert result["tp"] == 0
    assert result["fp"] == 0
    assert result["fn"] == 0
    assert result["tn"] == 0
    assert result["precision"] is None
    assert result["recall"] is None
    assert result["f1"] is None


def test_excluded_predictions_are_counted():
    report = evaluate(make_labels(), make_predictions())

    assert report["n_labeled"] == 3
    assert report["methods"]["checkov_detected"]["n_scored"] == 3
    assert report["methods"]["checkov_detected"]["n_excluded"] == 0
    assert report["methods"]["llm_detected"]["n_scored"] == 2
    assert report["methods"]["llm_detected"]["n_excluded"] == 1


def test_missing_prediction_case_is_rejected():
    labels = make_labels()
    predictions = make_predictions().iloc[:2]

    with pytest.raises(ValueError, match="Case ID mismatch"):
        evaluate(labels, predictions)


def test_unexpected_prediction_case_is_rejected():
    labels = make_labels()
    predictions = make_predictions()
    predictions.loc[2, "case_id"] = "UNKNOWN"

    with pytest.raises(ValueError, match="Case ID mismatch"):
        evaluate(labels, predictions)


def test_invalid_prediction_value_is_rejected():
    labels = make_labels()
    predictions = make_predictions()
    predictions.loc[0, "llm_detected"] = "maybe"

    with pytest.raises(ValueError, match="invalid values"):
        evaluate(labels, predictions)


def test_duplicate_case_id_is_rejected():
    labels = make_labels()
    labels.loc[1, "case_id"] = "TF001"

    with pytest.raises(ValueError, match="duplicate case_id"):
        evaluate(labels, make_predictions())
