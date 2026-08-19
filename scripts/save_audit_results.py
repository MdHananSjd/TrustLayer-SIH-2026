import json
from pathlib import Path

from governance_engine.audit_runner import (
    audit_model_from_files,
)


BASE_DIR = Path(__file__).resolve().parent.parent

ASSETS_DIR = BASE_DIR / "demo-assets"
MODELS_DIR = BASE_DIR / "demo-models"

OUTPUT_DIR = (
    ASSETS_DIR
    / "cached-results"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


def save_result(
    model_filename,
    metadata_filename,
    output_filename,
):

    result = audit_model_from_files(
        model_path=(
            MODELS_DIR
            / model_filename
        ),

        evaluation_csv_path=(
            ASSETS_DIR
            / "test_03.csv"
        ),

        metadata_path=(
            ASSETS_DIR
            / metadata_filename
        ),

        sensitive_attribute="gender",

        intersectional_attributes=[
            "gender",
            "age_group",
        ],

        proxy_threshold=0.5,

        min_intersection_group_size=10,
    )

    output_path = (
        OUTPUT_DIR
        / output_filename
    )

    with open(
        output_path,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            result,
            file,
            indent=2,
            default=str,
        )

    print(
        f"Saved {output_path}"
    )


if __name__ == "__main__":

    save_result(
        "biased_model_03.pkl",
        "biased_metadata_03.json",
        "biased_audit_03.json",
    )

    save_result(
        "improved_model_03.pkl",
        "improved_metadata_03.json",
        "improved_audit_03.json",
    )