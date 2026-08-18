import json
from pathlib import Path

from governance_engine.audit_runner import (
    audit_model_from_files,
)


BASE_DIR = Path(__file__).resolve().parent.parent
DEMO_DIR = BASE_DIR / "demo-assets"
OUTPUT_DIR = DEMO_DIR / "cached-results"

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


def save_result(
    model_filename,
    output_filename,
):

    result = audit_model_from_files(
        model_path=DEMO_DIR
        / model_filename,

        evaluation_csv_path=DEMO_DIR
        / "evaluation.csv",

        metadata_path=DEMO_DIR
        / "model_metadata.json",

        sensitive_attribute="gender",

        proxy_threshold=0.5,
    )

    output_path = OUTPUT_DIR / output_filename

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
        "biased_model.pkl",
        "biased_audit.json",
    )

    save_result(
        "improved_model.pkl",
        "improved_audit.json",
    )