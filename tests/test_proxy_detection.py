import pandas as pd
import pytest

from governance_engine.proxy_detection import (
    cramers_v,
    correlation_ratio,
    detect_proxy_features,
)
def test_cramers_v_detects_strong_association():

    gender = [
        "M", "M", "M", "M",
        "F", "F", "F", "F",
    ]

    region = [
        "A", "A", "A", "A",
        "B", "B", "B", "B",
    ]

    result = cramers_v(
        gender,
        region,
    )

    assert result == pytest.approx(
        1.0
    )
def test_cramers_v_detects_low_association():

    gender = [
        "M", "M", "M", "M",
        "F", "F", "F", "F",
    ]

    region = [
        "A", "A", "B", "B",
        "A", "A", "B", "B",
    ]

    result = cramers_v(
        gender,
        region,
    )

    assert result == pytest.approx(
        0.0
    )
def test_correlation_ratio_detects_strong_numeric_association():

    gender = [
        "M", "M", "M", "M",
        "F", "F", "F", "F",
    ]

    income = [
        80, 82, 78, 81,
        20, 22, 18, 21,
    ]

    result = correlation_ratio(
        gender,
        income,
    )

    assert result > 0.9
def test_detect_proxy_features():

    df = pd.DataFrame(
        {
            "gender": [
                "M", "M", "M", "M",
                "F", "F", "F", "F",
            ],

            "region": [
                "A", "A", "A", "A",
                "B", "B", "B", "B",
            ],

            "income": [
                80, 82, 78, 81,
                20, 22, 18, 21,
            ],

            "debt_ratio": [
                0.20, 0.50, 0.30, 0.40,
                0.21, 0.49, 0.31, 0.39,
            ],

            "approved": [
                1, 1, 1, 1,
                0, 0, 0, 0,
            ],
        }
    )

    result = detect_proxy_features(
        dataframe=df,
        sensitive_attribute="gender",
        exclude_columns=[
            "approved"
        ],
        threshold=0.8,
    )

    flagged_names = [
        item["feature"]
        for item
        in result["flagged_features"]
    ]

    assert "region" in flagged_names

    assert "income" in flagged_names

    assert "approved" not in flagged_names