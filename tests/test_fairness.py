import pytest

from governance_engine.fairness import (
    evaluate_fairness,
)


def test_basic_fairness_metrics():

    y_true = [
        1, 1, 0, 0,
        1, 1, 0, 0,
    ]

    y_pred = [
        1, 1, 1, 0,
        1, 0, 0, 0,
    ]

    sensitive = [
        "M", "M", "M", "M",
        "F", "F", "F", "F",
    ]

    result = evaluate_fairness(
        y_true=y_true,
        y_pred=y_pred,
        sensitive=sensitive,
        positive_label=1,
    )

    # -------------------------------------------------
    # Group metrics
    # -------------------------------------------------

    assert result["groups"]["M"][
        "selection_rate"
    ] == pytest.approx(
        0.75
    )

    assert result["groups"]["F"][
        "selection_rate"
    ] == pytest.approx(
        0.25
    )

    assert result["groups"]["M"][
        "tpr"
    ] == pytest.approx(
        1.0
    )

    assert result["groups"]["F"][
        "tpr"
    ] == pytest.approx(
        0.5
    )

    # -------------------------------------------------
    # Overall group disparity metrics
    # -------------------------------------------------

    assert result[
        "demographic_parity_gap"
    ] == pytest.approx(
        0.50
    )

    assert result[
        "disparate_impact_ratio"
    ] == pytest.approx(
        1 / 3
    )

    assert result[
        "tpr_gap"
    ] == pytest.approx(
        0.50
    )
def test_empty_input_raises_error():

    with pytest.raises(ValueError):

        evaluate_fairness(
            y_true=[],
            y_pred=[],
            sensitive=[],
        )
def test_sensitive_length_mismatch():

    with pytest.raises(ValueError):

        evaluate_fairness(
            y_true=[1, 0, 1],
            y_pred=[1, 0, 1],
            sensitive=["M", "F"],
        )
def test_requires_at_least_two_groups():

    with pytest.raises(ValueError):

        evaluate_fairness(
            y_true=[1, 0, 1, 0],
            y_pred=[1, 0, 1, 0],
            sensitive=[
                "M",
                "M",
                "M",
                "M",
            ],
        )
from governance_engine.fairness import (
    evaluate_fairness,
    evaluate_intersectional_fairness,
)
def test_intersectional_fairness():

    y_true = [
        1, 1,
        1, 1,
        1, 1,
        1, 1,
    ]

    y_pred = [
        1, 1,   # M <30
        1, 1,   # F <30

        1, 1,   # M >45
        0, 0,   # F >45
    ]

    gender = [
        "M", "M",
        "F", "F",
        "M", "M",
        "F", "F",
    ]

    age_group = [
        "<30", "<30",
        "<30", "<30",
        ">45", ">45",
        ">45", ">45",
    ]

    result = evaluate_intersectional_fairness(
        y_true=y_true,
        y_pred=y_pred,
        sensitive_attributes={
            "gender": gender,
            "age_group": age_group,
        },
        positive_label=1,
        min_group_size=2,
    )

    assert result[
        "subgroups"
    ][
        "gender=F | age_group=>45"
    ][
        "selection_rate"
    ] == pytest.approx(
        0.0
    )

    assert result[
        "subgroups"
    ][
        "gender=M | age_group=>45"
    ][
        "selection_rate"
    ] == pytest.approx(
        1.0
    )

    assert result[
        "largest_selection_gap"
    ] == pytest.approx(
        1.0
    )