from pathlib import Path

from governance_engine.artifact_loader import (
    load_metadata,
    load_evaluation_data,
    load_model,
    validate_artifact_contract,
)
from governance_engine.prediction import (
    prepare_predictions,
)
from governance_engine.evaluator import (
    run_evaluation,
)


def audit_model_from_files(
    model_path,
    evaluation_csv_path,
    metadata_path,
    sensitive_attribute=None,
    intersectional_attributes=None,
    proxy_threshold=0.5,
    min_intersection_group_size=5,
):
    """
    Complete TrustLayer performance/fairness audit
    using files supplied by the model/data team.
    """

    model_path = Path(model_path)
    evaluation_csv_path = Path(
        evaluation_csv_path
    )
    metadata_path = Path(metadata_path)

    # ---------------------------------------------
    # Load artifacts
    # ---------------------------------------------

    metadata = load_metadata(
        metadata_path
    )

    dataframe = load_evaluation_data(
        evaluation_csv_path
    )

    model = load_model(
        model_path
    )

    # ---------------------------------------------
    # Validate contract
    # ---------------------------------------------

    validate_artifact_contract(
        dataframe=dataframe,
        metadata=metadata,
    )

    # ---------------------------------------------
    # Choose sensitive attribute
    # ---------------------------------------------

    if sensitive_attribute is None:

        sensitive_attributes = metadata[
            "sensitive_attributes"
        ]

        if not sensitive_attributes:
            raise ValueError(
                "No sensitive attributes were configured."
            )

        sensitive_attribute = (
            sensitive_attributes[0]
        )

    # ---------------------------------------------
    # Generate predictions
    # ---------------------------------------------

    prediction_data = prepare_predictions(
        model=model,
        dataframe=dataframe,
        metadata=metadata,
    )

    # ---------------------------------------------
    # Evaluate
    # ---------------------------------------------

    result = run_evaluation(
        y_true=prediction_data["y_true"],
        y_pred=prediction_data["y_pred"],
        y_score=prediction_data["y_score"],
        evaluation_dataframe=dataframe,
        sensitive_attribute=sensitive_attribute,
        positive_label=metadata[
            "positive_label"
        ],
        intersectional_attributes=
            intersectional_attributes,
        target_column=metadata["target"],
        all_sensitive_attributes=metadata[
            "sensitive_attributes"
        ],
        proxy_threshold=proxy_threshold,
        min_intersection_group_size=
            min_intersection_group_size,
    )

    # ---------------------------------------------
    # Add model metadata to result
    # ---------------------------------------------

    return {
        "model": {
            "model_id": metadata.get(
                "model_id"
            ),
            "name": metadata["name"],
            "version": metadata["version"],
            "owner": metadata.get("owner"),
            "domain": metadata.get("domain"),
            "model_type": metadata.get(
                "model_type"
            ),
        },

        **result,
    }