from typing import Any, Dict, Optional, Sequence

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
)


def evaluate_performance(
    y_true: Sequence,
    y_pred: Sequence,
    y_score: Optional[Sequence] = None,
    positive_label: Any = 1,
) -> Dict[str, Any]:
    """
    Evaluate the predictive performance of a binary classification model.

    Parameters
    ----------
    y_true:
        Ground-truth labels.

    y_pred:
        Final class predictions produced by the model.

    y_score:
        Optional probability/score for the positive class.
        Required for ROC-AUC.

    positive_label:
        Label representing the positive class.
        Defaults to 1.

    Returns
    -------
    dict
        JSON-serializable dictionary containing the model's
        performance metrics.
    """

    # ---------------------------------------------------------
    # 1. Basic validation
    # ---------------------------------------------------------

    if len(y_true) == 0:
        raise ValueError("y_true cannot be empty.")

    if len(y_true) != len(y_pred):
        raise ValueError(
            "y_true and y_pred must contain the same number of samples."
        )

    if y_score is not None and len(y_score) != len(y_true):
        raise ValueError(
            "y_score must contain the same number of samples as y_true."
        )

    # ---------------------------------------------------------
    # 2. Classification metrics
    # ---------------------------------------------------------

    accuracy = accuracy_score(
        y_true,
        y_pred,
    )

    precision = precision_score(
        y_true,
        y_pred,
        pos_label=positive_label,
        zero_division=0,
    )

    recall = recall_score(
        y_true,
        y_pred,
        pos_label=positive_label,
        zero_division=0,
    )

    f1 = f1_score(
        y_true,
        y_pred,
        pos_label=positive_label,
        zero_division=0,
    )

    # ---------------------------------------------------------
    # 3. Confusion matrix
    # ---------------------------------------------------------

    matrix = confusion_matrix(
        y_true,
        y_pred,
    )

    # ---------------------------------------------------------
    # 4. Build JSON-safe response
    # ---------------------------------------------------------

    result = {
        "accuracy": float(accuracy),
        "precision": float(precision),
        "recall": float(recall),
        "f1": float(f1),
        "confusion_matrix": matrix.tolist(),
    }

    # ---------------------------------------------------------
    # 5. ROC-AUC
    # ---------------------------------------------------------

    if y_score is not None:
        try:
            auc = roc_auc_score(
                y_true,
                y_score,
            )

            result["roc_auc"] = float(auc)

        except ValueError:
            # ROC-AUC cannot be calculated in some cases,
            # for example if y_true contains only one class.
            result["roc_auc"] = None

    else:
        result["roc_auc"] = None

    return result