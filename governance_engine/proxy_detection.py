from typing import Any, Dict, List

import numpy as np
import pandas as pd
from scipy.stats import chi2_contingency
def cramers_v(
    x,
    y,
) -> float:
    """
    Measure association between two categorical variables.

    Returns a value approximately between 0 and 1.

    0 -> weak/no association
    1 -> strong association
    """

    table = pd.crosstab(x, y)

    if table.empty:
        return 0.0

    chi2 = chi2_contingency(
        table,
        correction=False,
    )[0]

    n = table.values.sum()

    if n == 0:
        return 0.0

    rows, cols = table.shape

    denominator = min(
        rows - 1,
        cols - 1,
    )

    if denominator <= 0:
        return 0.0

    value = np.sqrt(
        chi2
        / (
            n
            * denominator
        )
    )

    return float(value)
def correlation_ratio(
    categories,
    measurements,
) -> float:
    """
    Measure association between a categorical variable
    and a numeric variable.

    Returns a value between 0 and 1.

    0 -> little/no association
    1 -> strong association
    """

    categories = np.asarray(categories)
    measurements = np.asarray(
        measurements,
        dtype=float,
    )

    if len(categories) == 0:
        return 0.0

    if len(categories) != len(measurements):
        raise ValueError(
            "categories and measurements must have "
            "the same number of samples."
        )

    overall_mean = np.mean(
        measurements
    )

    numerator = 0.0

    unique_categories = np.unique(
        categories
    )

    for category in unique_categories:

        group_values = measurements[
            categories == category
        ]

        if len(group_values) == 0:
            continue

        group_mean = np.mean(
            group_values
        )

        numerator += (
            len(group_values)
            * (
                group_mean
                - overall_mean
            ) ** 2
        )

    denominator = np.sum(
        (
            measurements
            - overall_mean
        ) ** 2
    )

    if denominator == 0:
        return 0.0

    eta_squared = (
        numerator
        / denominator
    )

    eta = np.sqrt(
        eta_squared
    )

    return float(eta)
def detect_proxy_features(
    dataframe: pd.DataFrame,
    sensitive_attribute: str,
    exclude_columns: List[str] | None = None,
    threshold: float = 0.5,
) -> Dict[str, Any]:
    """
    Scan non-sensitive features for statistical
    association with a sensitive attribute.

    Parameters
    ----------
    dataframe:
        Input dataframe.

    sensitive_attribute:
        Column treated as the sensitive attribute.

    exclude_columns:
        Columns that should not be evaluated.
        Example: target column or row ID.

    threshold:
        Association strength above which a feature
        is flagged for review.

    Returns
    -------
    dict
        JSON-serializable proxy analysis.
    """

    if sensitive_attribute not in dataframe.columns:
        raise ValueError(
            f"Sensitive attribute '{sensitive_attribute}' "
            "was not found in the dataframe."
        )

    if exclude_columns is None:
        exclude_columns = []

    sensitive = dataframe[
        sensitive_attribute
    ]

    results = []

    for column in dataframe.columns:

        if column == sensitive_attribute:
            continue

        if column in exclude_columns:
            continue

        feature = dataframe[column]

        # -----------------------------------------
        # Categorical feature
        # -----------------------------------------

        if (
            pd.api.types.is_string_dtype(feature)
            or
            isinstance(feature.dtype,pd.CategoricalDtype)
            or
            pd.api.types.is_bool_dtype(feature)
        ):

            association = cramers_v(
                sensitive,
                feature,
            )

            method = "cramers_v"

        # -----------------------------------------
        # Numeric feature
        # -----------------------------------------

        elif pd.api.types.is_numeric_dtype(
            feature
        ):

            association = correlation_ratio(
                sensitive,
                feature,
            )

            method = "correlation_ratio"

        else:

            # unsupported type for MVP
            continue

        results.append(
            {
                "feature": column,
                "association": float(
                    association
                ),
                "method": method,
                "flagged": bool(
                    association
                    >= threshold
                ),
            }
        )

    # Highest association first
    results.sort(
        key=lambda item:
            item["association"],
        reverse=True,
    )

    flagged = [
        item
        for item in results
        if item["flagged"]
    ]

    return {
        "sensitive_attribute":
            sensitive_attribute,

        "threshold":
            float(threshold),

        "features":
            results,

        "flagged_features":
            flagged,
    }