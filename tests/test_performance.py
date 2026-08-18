import pytest

from governance_engine.performance import evaluate_performance


def test_basic_binary_performance():

    y_true = [
        1,
        0,
        1,
        0,
        1,
    ]

    y_pred = [
        1,
        0,
        0,
        1,
        1,
    ]

    y_score = [
        0.91,
        0.20,
        0.42,
        0.74,
        0.88,
    ]

    result = evaluate_performance(
        y_true=y_true,
        y_pred=y_pred,
        y_score=y_score,
        positive_label=1,
    )

    assert result["accuracy"] == pytest.approx(
        0.60
    )

    assert result["precision"] == pytest.approx(
        2 / 3
    )

    assert result["recall"] == pytest.approx(
        2 / 3
    )

    assert result["f1"] == pytest.approx(
        2 / 3
    )

    assert result["confusion_matrix"] == [
        [1, 1],
        [1, 2],
    ]

    assert result["roc_auc"] is not None

def test_empty_y_true_raises_error():

    with pytest.raises(ValueError):

        evaluate_performance(
            y_true=[],
            y_pred=[],
        )

def test_mismatched_lengths_raise_error():

    with pytest.raises(ValueError):

        evaluate_performance(
            y_true=[1, 0, 1],
            y_pred=[1, 0],
        )
def test_missing_scores_returns_none_auc():

    result = evaluate_performance(
        y_true=[1, 0, 1, 0],
        y_pred=[1, 0, 1, 0],
    )

    assert result["roc_auc"] is None

