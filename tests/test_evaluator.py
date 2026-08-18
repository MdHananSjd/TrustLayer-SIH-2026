import pandas as pd
import pytest

from governance_engine.evaluator import (
    run_evaluation,
)


def test_full_evaluation_pipeline():

    df = pd.DataFrame(
        {
            "gender": [
                "M", "M", "M", "M",
                "F", "F", "F", "F",
            ],

            "age_group": [
                "<30", "<30", ">45", ">45",
                "<30", "<30", ">45", ">45",
            ],

            "income": [
                80, 82, 78, 81,
                20, 22, 18, 21,
            ],

            "region": [
                "A", "A", "A", "A",
                "B", "B", "B", "B",
            ],

            "approved": [
                1, 1, 0, 0,
                1, 1, 0, 0,
            ],
        }
    )

    y_true = [
        1, 1, 0, 0,
        1, 1, 0, 0,
    ]

    y_pred = [
        1, 1, 1, 0,
        1, 0, 0, 0,
    ]

    y_score = [
        0.90, 0.85, 0.75, 0.20,
        0.80, 0.40, 0.25, 0.10,
    ]

    result = run_evaluation(
        y_true=y_true,
        y_pred=y_pred,
        y_score=y_score,
        evaluation_dataframe=df,
        sensitive_attribute="gender",
        positive_label=1,
        intersectional_attributes=[
            "gender",
            "age_group",
        ],
        target_column="approved",
        proxy_threshold=0.8,
        min_intersection_group_size=2,
    )

    # -----------------------------------------
    # Performance
    # -----------------------------------------

    assert "performance" in result

    assert result[
        "performance"
    ][
        "accuracy"
    ] == pytest.approx(
        0.75
    )

    # -----------------------------------------
    # Fairness
    # -----------------------------------------

    assert "fairness" in result

    assert result[
        "fairness"
    ][
        "demographic_parity_gap"
    ] == pytest.approx(
        0.50
    )

    assert result[
        "fairness"
    ][
        "tpr_gap"
    ] == pytest.approx(
        0.50
    )

    # -----------------------------------------
    # Intersectional fairness
    # -----------------------------------------

    assert result[
        "fairness"
    ][
        "intersectional"
    ] is not None

    # -----------------------------------------
    # Proxy analysis
    # -----------------------------------------

    proxy = result[
        "fairness"
    ][
        "proxy_analysis"
    ]

    flagged_names = [
        item["feature"]
        for item
        in proxy["flagged_features"]
    ]

    assert "region" in flagged_names

    assert "income" in flagged_names

    assert "approved" not in flagged_names