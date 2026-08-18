import numpy as np


def prepare_predictions(
    model,
    dataframe,
    metadata,
):
    """
    Produce y_true, y_pred and y_score for TrustLayer evaluation.
    """

    feature_names = metadata["feature_names"]
    target_column = metadata["target"]
    positive_label = metadata["positive_label"]

    X = dataframe[feature_names]
    y_true = dataframe[target_column]

    # Final class prediction
    y_pred = model.predict(X)

    # Probability/decision score for positive class
    y_score = None

    if hasattr(model, "predict_proba"):

        probabilities = model.predict_proba(X)

        if not hasattr(model, "classes_"):
            raise ValueError(
                "Model exposes predict_proba but has no classes_ attribute."
            )

        classes = list(model.classes_)

        if positive_label not in classes:
            raise ValueError(
                f"Positive label {positive_label!r} "
                f"not found in model classes {classes}."
            )

        positive_index = classes.index(
            positive_label
        )

        y_score = probabilities[
            :,
            positive_index
        ]

    elif hasattr(model, "decision_function"):

        raw_scores = model.decision_function(X)

        raw_scores = np.asarray(raw_scores)

        # Binary classifiers generally return one score per row.
        if raw_scores.ndim == 1:
            y_score = raw_scores

    return {
        "X": X,
        "y_true": y_true,
        "y_pred": y_pred,
        "y_score": y_score,
    }