from typing import Any, Dict, Sequence

import numpy as np


def evaluate_fairness(
    y_true: Sequence,
    y_pred: Sequence,
    sensitive: Sequence,
    positive_label: Any = 1,
) -> Dict[str, Any]:
    """
    Evaluate group fairness for a binary classification model.

    Parameters
    ----------
    y_true:
        Ground-truth labels.

    y_pred:
        Final class predictions.

    sensitive:
        Sensitive attribute values corresponding to each sample.

    positive_label:
        Label representing the positive outcome.
        Defaults to 1.

    Returns
    -------
    dict
        JSON-serializable dictionary containing group fairness metrics.
    """

    # ---------------------------------------------------------
    # 1. Validation
    # ---------------------------------------------------------

    if len(y_true) == 0:
        raise ValueError("y_true cannot be empty.")

    if len(y_true) != len(y_pred):
        raise ValueError(
            "y_true and y_pred must contain the same number of samples."
        )

    if len(y_true) != len(sensitive):
        raise ValueError(
            "sensitive must contain the same number of samples as y_true."
        )

    # Convert inputs to NumPy arrays
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)
    sensitive = np.asarray(sensitive)

    # ---------------------------------------------------------
    # 2. Find groups
    # ---------------------------------------------------------

    unique_groups = np.unique(sensitive)

    if len(unique_groups) < 2:
        raise ValueError(
            "Fairness evaluation requires at least two sensitive groups."
        )

    groups = {}

    # ---------------------------------------------------------
    # 3. Per-group calculations
    # ---------------------------------------------------------

    for group in unique_groups:

        group_mask = sensitive == group

        group_true = y_true[group_mask]
        group_pred = y_pred[group_mask]

        group_count = len(group_true)

        # Selection rate
        positive_predictions = np.sum(
            group_pred == positive_label
        )

        selection_rate = (
            positive_predictions / group_count
        )

        # True Positive Rate
        actual_positive_mask = (
            group_true == positive_label
        )

        actual_positive_count = np.sum(
            actual_positive_mask
        )

        if actual_positive_count > 0:

            true_positives = np.sum(
                group_pred[actual_positive_mask]
                == positive_label
            )

            tpr = (
                true_positives
                / actual_positive_count
            )

        else:
            tpr = None

        groups[str(group)] = {
            "count": int(group_count),
            "selection_rate": float(selection_rate),
            "tpr": (
                None
                if tpr is None
                else float(tpr)
            ),
        }

    # ---------------------------------------------------------
    # 4. Demographic parity gap
    # ---------------------------------------------------------

    selection_rates = [
        metrics["selection_rate"]
        for metrics in groups.values()
    ]

    demographic_parity_gap = (
        max(selection_rates)
        - min(selection_rates)
    )

    # ---------------------------------------------------------
    # 5. Disparate impact ratio
    # ---------------------------------------------------------

    highest_rate = max(selection_rates)
    lowest_rate = min(selection_rates)

    if highest_rate > 0:
        disparate_impact_ratio = (
            lowest_rate / highest_rate
        )
    else:
        disparate_impact_ratio = None

    # ---------------------------------------------------------
    # 6. Equal opportunity / TPR gap
    # ---------------------------------------------------------

    valid_tprs = [
        metrics["tpr"]
        for metrics in groups.values()
        if metrics["tpr"] is not None
    ]

    if len(valid_tprs) >= 2:
        tpr_gap = (
            max(valid_tprs)
            - min(valid_tprs)
        )
    else:
        tpr_gap = None

    # ---------------------------------------------------------
    # 7. Return JSON-safe result
    # ---------------------------------------------------------

    return {
        "groups": groups,

        "demographic_parity_gap": float(
            demographic_parity_gap
        ),

        "disparate_impact_ratio": (
            None
            if disparate_impact_ratio is None
            else float(disparate_impact_ratio)
        ),

        "tpr_gap": (
            None
            if tpr_gap is None
            else float(tpr_gap)
        ),

    }
def create_age_groups(age_values):
    """
    Convert numeric ages into simple demographic buckets.

    Buckets:
        <30
        30-45
        >45
    """

    age_values = np.asarray(age_values)

    groups = []

    for age in age_values:

        if age < 30:
            groups.append("<30")

        elif age <= 45:
            groups.append("30-45")

        else:
            groups.append(">45")

    return np.asarray(groups)
def evaluate_intersectional_fairness(
    y_true,
    y_pred,
    sensitive_attributes,
    positive_label=1,
    min_group_size=5,
):
    """
    Evaluate fairness across combinations of multiple
    sensitive attributes.

    Example:
        gender x age_group

    Parameters
    ----------
    y_true:
        Ground-truth labels.

    y_pred:
        Model predictions.

    sensitive_attributes:
        Dictionary mapping attribute names to values.

        Example:
        {
            "gender": ["M", "F", ...],
            "age_group": ["<30", ">45", ...]
        }

    positive_label:
        Positive outcome label.

    min_group_size:
        Ignore groups smaller than this value.

    Returns
    -------
    dict
        JSON-safe dictionary containing subgroup metrics.
    """

    if len(y_true) == 0:
        raise ValueError("y_true cannot be empty.")

    if len(sensitive_attributes) < 2:
        raise ValueError(
            "Intersectional analysis requires at least two attributes."
        )

    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)

    attribute_names = list(
        sensitive_attributes.keys()
    )

    attribute_arrays = []

    for name in attribute_names:

        values = np.asarray(
            sensitive_attributes[name]
        )

        if len(values) != len(y_true):
            raise ValueError(
                f"{name} must contain the same "
                "number of samples as y_true."
            )

        attribute_arrays.append(values)

    intersection_labels = []

    for values in zip(*attribute_arrays):

        label = " | ".join(
            f"{name}={value}"
            for name, value
            in zip(attribute_names, values)
        )

        intersection_labels.append(label)

    intersection_labels = np.asarray(
        intersection_labels
    )

    unique_groups = np.unique(
        intersection_labels
    )

    subgroup_results = {}

    for group in unique_groups:

        mask = intersection_labels == group

        group_count = int(
            np.sum(mask)
        )

        if group_count < min_group_size:
            continue

        group_true = y_true[mask]
        group_pred = y_pred[mask]

        selection_rate = float(
            np.mean(
                group_pred == positive_label
            )
        )

        actual_positive_mask = (
            group_true == positive_label
        )

        positive_count = int(
            np.sum(actual_positive_mask)
        )

        if positive_count > 0:

            tpr = float(
                np.mean(
                    group_pred[
                        actual_positive_mask
                    ] == positive_label
                )
            )

        else:
            tpr = None

        subgroup_results[group] = {
            "count": group_count,
            "selection_rate": selection_rate,
            "tpr": tpr,
        }

    if len(subgroup_results) < 2:

        return {
            "subgroups": subgroup_results,
            "worst_selection_rate_group": None,
            "largest_selection_gap": None,
        }

    rates = {
        name: metrics["selection_rate"]
        for name, metrics
        in subgroup_results.items()
    }

    lowest_group = min(
        rates,
        key=rates.get,
    )

    highest_group = max(
        rates,
        key=rates.get,
    )

    largest_gap = (
        rates[highest_group]
        - rates[lowest_group]
    )

    return {
        "subgroups": subgroup_results,

        "worst_selection_rate_group": {
            "group": lowest_group,
            "selection_rate": float(
                rates[lowest_group]
            ),
        },

        "best_selection_rate_group": {
            "group": highest_group,
            "selection_rate": float(
                rates[highest_group]
            ),
        },

        "largest_selection_gap": float(
            largest_gap
        ),
    }
