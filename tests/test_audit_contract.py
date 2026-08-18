import json
from pathlib import Path

import pytest

from governance_engine.audit_runner import (
    audit_model_from_files,
)


BASE_DIR = Path(__file__).resolve().parent.parent

ASSETS_DIR = BASE_DIR / "demo-assets"
MODELS_DIR = BASE_DIR / "demo-models"


@pytest.mark.skipif(
    not (
        MODELS_DIR
        / "biased_model_02.pkl"
    ).exists(),
    reason="Demo model artifacts are unavailable.",
)
def test_audit_contract():

    result = audit_model_from_files(
        model_path=(
            MODELS_DIR
            / "biased_model_02.pkl"
        ),

        evaluation_csv_path=(
            ASSETS_DIR
            / "test_02.csv"
        ),

        metadata_path=(
            ASSETS_DIR
            / "biased_metadata_02.json"
        ),

        sensitive_attribute="gender",

        intersectional_attributes=[
            "gender",
            "age_group",
        ],

        min_intersection_group_size=10,
    )

    # ---------------------------------------------------------
    # Top-level API contract
    # ---------------------------------------------------------

    assert "model" in result
    assert "performance" in result
    assert "fairness" in result

    # ---------------------------------------------------------
    # Performance contract
    # ---------------------------------------------------------

    performance = result[
        "performance"
    ]

    required_performance = [
        "accuracy",
        "precision",
        "recall",
        "f1",
        "roc_auc",
        "confusion_matrix",
    ]

    for field in required_performance:
        assert field in performance

    # ---------------------------------------------------------
    # Fairness contract
    # ---------------------------------------------------------

    fairness = result[
        "fairness"
    ]

    required_fairness = [
        "groups",
        "demographic_parity_gap",
        "disparate_impact_ratio",
        "tpr_gap",
        "sensitive_attribute",
        "intersectional",
        "proxy_analysis",
    ]

    for field in required_fairness:
        assert field in fairness

    # ---------------------------------------------------------
    # Must be JSON serializable
    # ---------------------------------------------------------

    serialized = json.dumps(
        result
    )

    assert isinstance(
        serialized,
        str,
    )