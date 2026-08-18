from typing import Any

import pandas as pd

from governance_engine.performance import evaluate_performance
from governance_engine.fairness import (
    evaluate_fairness,
    evaluate_intersectional_fairness,
)
from governance_engine.proxy_detection import detect_proxy_features


def run_evaluation(
    y_true,
    y_pred,
    evaluation_dataframe: pd.DataFrame,
    sensitive_attribute: str,
    y_score=None,
    positive_label: Any = 1,
    intersectional_attributes: list[str] | None = None,
    target_column: str | None = None,
    proxy_threshold: float = 0.5,
    min_intersection_group_size: int = 5,
):
    """
    Run the complete TrustLayer performance and fairness audit.

    Parameters
    ----------
    y_true:
        Ground-truth labels.

    y_pred:
        Model predictions.

    evaluation_dataframe:
        Evaluation dataset containing model features and
        sensitive attributes.

    sensitive_attribute:
        Main sensitive attribute to audit.

    y_score:
        Optional probability/score for the positive class.

    positive_label:
        Label representing the positive outcome.

    intersectional_attributes:
        Optional list of sensitive/demographic columns to
        combine for intersectional analysis.

        Example:
        ["gender", "age_group"]

    target_column:
        Optional target column that should be excluded from
        proxy-feature scanning.

    proxy_threshold:
        Association threshold above which a feature is
        flagged for proxy review.

    min_intersection_group_size:
        Smallest subgroup size allowed in intersectional
        analysis.

    Returns
    -------
    dict
        JSON-serializable performance and fairness audit.
    """

    # ---------------------------------------------------------
    # 1. Validate dataframe
    # ---------------------------------------------------------

    if sensitive_attribute not in evaluation_dataframe.columns:
        raise ValueError(
            f"Sensitive attribute '{sensitive_attribute}' "
            "was not found in evaluation_dataframe."
        )

    if len(evaluation_dataframe) != len(y_true):
        raise ValueError(
            "evaluation_dataframe must contain the same "
            "number of rows as y_true."
        )

    if len(y_pred) != len(y_true):
        raise ValueError(
            "y_pred must contain the same number of "
            "samples as y_true."
        )

    # ---------------------------------------------------------
    # 2. Performance audit
    # ---------------------------------------------------------

    performance_result = evaluate_performance(
        y_true=y_true,
        y_pred=y_pred,
        y_score=y_score,
        positive_label=positive_label,
    )

    # ---------------------------------------------------------
    # 3. Basic fairness audit
    # ---------------------------------------------------------

    sensitive_values = evaluation_dataframe[
        sensitive_attribute
    ]

    fairness_result = evaluate_fairness(
        y_true=y_true,
        y_pred=y_pred,
        sensitive=sensitive_values,
        positive_label=positive_label,
    )

    fairness_result[
        "sensitive_attribute"
    ] = sensitive_attribute

    # ---------------------------------------------------------
    # 4. Intersectional fairness
    # ---------------------------------------------------------

    intersectional_result = None

    if intersectional_attributes:

        missing_columns = [
            column
            for column in intersectional_attributes
            if column not in evaluation_dataframe.columns
        ]

        if missing_columns:
            raise ValueError(
                "Intersectional attributes not found: "
                + ", ".join(missing_columns)
            )

        if len(intersectional_attributes) >= 2:

            intersectional_data = {
                column:
                    evaluation_dataframe[
                        column
                    ].tolist()

                for column
                in intersectional_attributes
            }

            intersectional_result = (
                evaluate_intersectional_fairness(
                    y_true=y_true,
                    y_pred=y_pred,
                    sensitive_attributes=
                        intersectional_data,
                    positive_label=
                        positive_label,
                    min_group_size=
                        min_intersection_group_size,
                )
            )

    # ---------------------------------------------------------
    # 5. Proxy-feature analysis
    # ---------------------------------------------------------

    exclude_columns = []

    if target_column is not None:
        exclude_columns.append(
            target_column
        )

    proxy_result = detect_proxy_features(
        dataframe=evaluation_dataframe,
        sensitive_attribute=
            sensitive_attribute,
        exclude_columns=
            exclude_columns,
        threshold=
            proxy_threshold,
    )

    # ---------------------------------------------------------
    # 6. Final JSON-safe result
    # ---------------------------------------------------------

    return {
        "performance": performance_result,

        "fairness": {
            **fairness_result,

            "intersectional":
                intersectional_result,

            "proxy_analysis":
                proxy_result,
        },
    }