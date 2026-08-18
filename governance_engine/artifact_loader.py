import json
from pathlib import Path

import joblib
import pandas as pd


def load_metadata(metadata_path):
    """
    Load and validate TrustLayer model metadata.
    """

    metadata_path = Path(metadata_path)

    if not metadata_path.exists():
        raise FileNotFoundError(
            f"Metadata file not found: {metadata_path}"
        )

    with open(metadata_path, "r", encoding="utf-8") as file:
        metadata = json.load(file)

    required_fields = [
        "name",
        "version",
        "target",
        "positive_label",
        "sensitive_attributes",
        "feature_names",
    ]

    missing = [
        field
        for field in required_fields
        if field not in metadata
    ]

    if missing:
        raise ValueError(
            "Metadata is missing required fields: "
            + ", ".join(missing)
        )

    return metadata


def load_evaluation_data(csv_path):
    """
    Load evaluation CSV.
    """

    csv_path = Path(csv_path)

    if not csv_path.exists():
        raise FileNotFoundError(
            f"Evaluation CSV not found: {csv_path}"
        )

    dataframe = pd.read_csv(csv_path)

    if dataframe.empty:
        raise ValueError(
            "Evaluation dataset is empty."
        )

    return dataframe


def load_model(model_path):
    """
    Load a serialized scikit-learn compatible model/pipeline.
    """

    model_path = Path(model_path)

    if not model_path.exists():
        raise FileNotFoundError(
            f"Model file not found: {model_path}"
        )

    model = joblib.load(model_path)

    return model


def validate_artifact_contract(
    dataframe,
    metadata,
):
    """
    Ensure the evaluation CSV satisfies the model metadata contract.
    """

    target = metadata["target"]
    feature_names = metadata["feature_names"]
    sensitive_attributes = metadata[
        "sensitive_attributes"
    ]

    required_columns = (
        feature_names
        + sensitive_attributes
        + [target]
    )

    missing_columns = [
        column
        for column in required_columns
        if column not in dataframe.columns
    ]

    if missing_columns:
        raise ValueError(
            "Evaluation data is missing required columns: "
            + ", ".join(sorted(set(missing_columns)))
        )

    return True