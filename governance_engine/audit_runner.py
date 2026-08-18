from pathlib import Path

from governance_engine.artifact_loader import (
    load_metadata,
    load_evaluation_data,
    load_model,
    validate_artifact_contract,
)

from governance_engine.preprocessing import (
    add_age_group,
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
    Run a complete TrustLayer performance and fairness audit
    using model/data artifacts supplied by the model team.

    Parameters
    ----------
    model_path:
        Path to serialized sklearn Pipeline/model.

    evaluation_csv_path:
        Path to held-out evaluation dataset.

    metadata_path:
        Path to metadata JSON describing this model.

    sensitive_attribute:
        Sensitive attribute to audit.
        If omitted, the first configured sensitive attribute
        from metadata is used.

    intersectional_attributes:
        Optional list of columns for intersectional analysis.
        Example:
            ["gender", "age_group"]

    proxy_threshold:
        Association threshold used by proxy detection.

    min_intersection_group_size:
        Smallest group included in intersectional analysis.

    Returns
    -------
    dict
        JSON-serializable audit result containing:

        model
        performance
        fairness
    """

    # =========================================================
    # 1. Normalize paths
    # =========================================================

    model_path = Path(model_path)

    evaluation_csv_path = Path(
        evaluation_csv_path
    )

    metadata_path = Path(
        metadata_path
    )

    # =========================================================
    # 2. Load metadata
    # =========================================================

    metadata = load_metadata(
        metadata_path
    )

    # =========================================================
    # 3. Load evaluation data
    # =========================================================

    dataframe = load_evaluation_data(
        evaluation_csv_path
    )
    if "age" in dataframe.columns:
        dataframe = add_age_group(
            dataframe
        )

    # =========================================================
    # 4. Load trained model / sklearn Pipeline
    # =========================================================

    model = load_model(
        model_path
    )

    # =========================================================
    # 5. Validate metadata ↔ CSV contract
    # =========================================================

    validate_artifact_contract(
        dataframe=dataframe,
        metadata=metadata,
    )

    # =========================================================
    # 6. Determine sensitive attribute
    # =========================================================

    configured_sensitive_attributes = (
        metadata.get(
            "sensitive_attributes",
            [],
        )
    )

    if sensitive_attribute is None:

        if not configured_sensitive_attributes:

            raise ValueError(
                "No sensitive attributes are configured "
                "in model metadata."
            )

        sensitive_attribute = (
            configured_sensitive_attributes[0]
        )

    if (
        sensitive_attribute
        not in configured_sensitive_attributes
    ):

        raise ValueError(
            f"Sensitive attribute "
            f"'{sensitive_attribute}' "
            "is not configured in metadata. "
            f"Configured attributes: "
            f"{configured_sensitive_attributes}"
        )

    if (
        sensitive_attribute
        not in dataframe.columns
    ):

        raise ValueError(
            f"Sensitive attribute "
            f"'{sensitive_attribute}' "
            "does not exist in evaluation data."
        )

    # =========================================================
    # 7. Generate predictions
    # =========================================================

    prediction_data = prepare_predictions(
        model=model,
        dataframe=dataframe,
        metadata=metadata,
    )

    # prediction_data contains:
    #
    # X
    # y_true
    # y_pred
    # y_score

    # =========================================================
    # 8. Run performance + fairness engine
    # =========================================================

    evaluation_result = run_evaluation(

        y_true=prediction_data[
            "y_true"
        ],

        y_pred=prediction_data[
            "y_pred"
        ],

        y_score=prediction_data[
            "y_score"
        ],

        evaluation_dataframe=dataframe,

        sensitive_attribute=
            sensitive_attribute,

        positive_label=
            metadata[
                "positive_label"
            ],

        intersectional_attributes=
            intersectional_attributes,

        target_column=
            metadata[
                "target"
            ],

        all_sensitive_attributes=
            configured_sensitive_attributes,

        proxy_threshold=
            proxy_threshold,

        min_intersection_group_size=
            min_intersection_group_size,
    )

    # =========================================================
    # 9. Build model metadata section
    # =========================================================

    model_information = {

        "model_id":
            metadata.get(
                "model_id"
            ),

        "name":
            metadata.get(
                "name"
            ),

        "version":
            metadata.get(
                "version"
            ),

        "owner":
            metadata.get(
                "owner"
            ),

        "domain":
            metadata.get(
                "domain"
            ),

        "model_type":
            metadata.get(
                "model_type"
            ),

        "target":
            metadata.get(
                "target"
            ),

        "positive_label":
            metadata.get(
                "positive_label"
            ),

        "sensitive_attributes":
            configured_sensitive_attributes,

        "feature_names":
            metadata.get(
                "feature_names",
                [],
            ),

        "model_file":
            model_path.name,

        "evaluation_file":
            evaluation_csv_path.name,
    }

    # =========================================================
    # 10. Final audit result
    # =========================================================

    audit_result = {

        "model":
            model_information,

        "performance":
            evaluation_result[
                "performance"
            ],

        "fairness":
            evaluation_result[
                "fairness"
            ],
    }

    return audit_result