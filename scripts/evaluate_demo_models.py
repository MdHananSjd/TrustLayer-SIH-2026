import json
from pathlib import Path

from governance_engine.audit_runner import (
    audit_model_from_files,
)


BASE_DIR = Path(__file__).resolve().parent.parent

ASSETS_DIR = BASE_DIR / "demo-assets"
MODELS_DIR = BASE_DIR / "demo-models"


def run_and_print(
    name,
    model_filename,
    metadata_filename,
):

    print()
    print("=" * 70)
    print(name)
    print("=" * 70)

    result = audit_model_from_files(

        model_path=(
            MODELS_DIR
            / model_filename
        ),

        evaluation_csv_path=(
            ASSETS_DIR
            / "test_02.csv"
        ),

        metadata_path=(
            ASSETS_DIR
            / metadata_filename
        ),

        sensitive_attribute="gender",

        proxy_threshold=0.5,

        min_intersection_group_size=10,
    )

    print(
        json.dumps(
            result,
            indent=2,
            default=str,
        )
    )

    return result


if __name__ == "__main__":

    biased_result = run_and_print(
        "BIASED MODEL",
        "biased_model_02.pkl",
        "biased_metadata_02.json",
    )

    improved_result = run_and_print(
        "IMPROVED MODEL",
        "improved_model_02.pkl",
        "improved_metadata_02.json",
    )

    print()
    print("=" * 70)
    print("BEFORE / AFTER SUMMARY")
    print("=" * 70)

    print(
        "Biased accuracy:",
        biased_result["performance"]["accuracy"],
    )

    print(
        "Improved accuracy:",
        improved_result["performance"]["accuracy"],
    )

    print(
        "Biased DP gap:",
        biased_result["fairness"][
            "demographic_parity_gap"
        ],
    )

    print(
        "Improved DP gap:",
        improved_result["fairness"][
            "demographic_parity_gap"
        ],
    )

    print(
        "Biased TPR gap:",
        biased_result["fairness"][
            "tpr_gap"
        ],
    )

    print(
        "Improved TPR gap:",
        improved_result["fairness"][
            "tpr_gap"
        ],
    )