from typing import Any

import pandas as pd

from governance_engine.performance import (
    evaluate_performance,
)

from governance_engine.fairness import (
    evaluate_fairness,
    evaluate_intersectional_fairness,
)

from governance_engine.proxy_detection import (
    detect_proxy_features,
)


def run_evaluation(
    y_true,
    y_pred,
    evaluation_dataframe: pd.DataFrame,
    sensitive_attribute: str,
    y_score=None,
    positive_label: Any = 1,
    intersectional_attributes: list[str] | None = None,
    target_column: str | None = None,
    all_sensitive_attributes: list[str] | None = None,
    proxy_threshold: float = 0.5,
    min_intersection_group_size: int = 5,
):
    """
    Run the complete performance and fairness evaluation.

    This function is the main orchestration layer for the
    fairness/evaluation module.

    It combines:

    - predictive performance
    - basic group fairness
    - optional intersectional fairness
    - potential proxy-feature analysis

    It returns JSON-serializable data for the backend.
    """

    # =========================================================
    # 1. Basic validation
    # =========================================================

    if len(y_true) == 0:
        raise ValueError(
            "y_true cannot be empty."
        )

    if len(y_true) != len(y_pred):
        raise ValueError(
            "y_true and y_pred must contain "
            "the same number of samples."
        )

    if len(evaluation_dataframe) != len(y_true):
        raise ValueError(
            "evaluation_dataframe and y_true must "
            "contain the same number of rows."
        )

    if (
        sensitive_attribute
        not in evaluation_dataframe.columns
    ):
        raise ValueError(
            f"Sensitive attribute "
            f"'{sensitive_attribute}' "
            "was not found in the evaluation dataframe."
        )

    # =========================================================
    # 2. Performance evaluation
    # =========================================================

    performance_result = evaluate_performance(
        y_true=y_true,
        y_pred=y_pred,
        y_score=y_score,
        positive_label=positive_label,
    )

    # =========================================================
    # 3. Basic fairness evaluation
    # =========================================================

    sensitive_values = (
        evaluation_dataframe[
            sensitive_attribute
        ]
    )

    fairness_result = evaluate_fairness(
        y_true=y_true,
        y_pred=y_pred,
        sensitive=sensitive_values,
        positive_label=positive_label,
    )

    fairness_result[
        "sensitive_attribute"
    ] = sensitive_attribute

    # =========================================================
    # 4. Intersectional analysis
    # =========================================================

    intersectional_result = None

    if intersectional_attributes:

        if len(intersectional_attributes) < 2:
            raise ValueError(
                "Intersectional fairness requires "
                "at least two attributes."
            )

        missing_columns = [
            column
            for column
            in intersectional_attributes
            if column
            not in evaluation_dataframe.columns
        ]

        if missing_columns:
            raise ValueError(
                "Missing intersectional attributes: "
                + ", ".join(
                    missing_columns
                )
            )

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

    # =========================================================
    # 5. Build proxy exclusion list
    # =========================================================

    excluded_columns = []

    # Do not scan the target as a potential proxy.
    if target_column is not None:
        excluded_columns.append(
            target_column
        )

    # Do not treat known sensitive attributes as
    # ordinary proxy candidates.
    if all_sensitive_attributes:

        excluded_columns.extend(
            all_sensitive_attributes
        )

    # Remove duplicates.
    excluded_columns = list(
        set(
            excluded_columns
        )
    )

    # =========================================================
    # 6. Proxy-feature analysis
    # =========================================================

    proxy_result = detect_proxy_features(
        dataframe=
            evaluation_dataframe,

        sensitive_attribute=
            sensitive_attribute,

        exclude_columns=
            excluded_columns,

        threshold=
            proxy_threshold,
    )

    # =========================================================
    # 7. Final output
    # =========================================================

    return {

        "performance":
            performance_result,

        "fairness": {

            **fairness_result,

            "intersectional":
                intersectional_result,

            "proxy_analysis":
                proxy_result,
        },
    }