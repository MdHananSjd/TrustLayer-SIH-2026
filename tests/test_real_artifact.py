from pathlib import Path

from governance_engine.audit_runner import (
    audit_model_from_files,
)


BASE_DIR = Path(__file__).resolve().parent.parent

ASSETS_DIR = BASE_DIR / "demo-assets"
MODELS_DIR = BASE_DIR / "demo-models"


def test_biased_model_real_artifact():

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
    )

    assert "model" in result
    assert "performance" in result
    assert "fairness" in result

    assert (
        "accuracy"
        in result["performance"]
    )

    assert (
        "demographic_parity_gap"
        in result["fairness"]
    )

    assert (
        "disparate_impact_ratio"
        in result["fairness"]
    )

    assert (
        "tpr_gap"
        in result["fairness"]
    )


def test_improved_model_real_artifact():

    result = audit_model_from_files(

        model_path=(
            MODELS_DIR
            / "improved_model_02.pkl"
        ),

        evaluation_csv_path=(
            ASSETS_DIR
            / "test_02.csv"
        ),

        metadata_path=(
            ASSETS_DIR
            / "improved_metadata_02.json"
        ),

        sensitive_attribute="gender",
    )

    assert "model" in result
    assert "performance" in result
    assert "fairness" in result

    assert (
        "accuracy"
        in result["performance"]
    )

    assert (
        "demographic_parity_gap"
        in result["fairness"]
    )