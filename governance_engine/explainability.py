import warnings

warnings.filterwarnings("ignore")

from typing import Any, Dict, List, Optional, Sequence, Tuple

import numpy as np
import pandas as pd
import shap
from sklearn.pipeline import Pipeline


# ---------------------------------------------------------
# 1. Version compatibility patch
# ---------------------------------------------------------

def _patch_version_gaps(
    estimator: Any,
) -> Any:
    """
    Restore sklearn attributes that newer training environments
    omit but older runtime environments still expect.

    sklearn 1.9.0 no longer sets ``self.multi_class`` on a fitted
    LogisticRegression (the parameter was deprecated). Older sklearn
    (e.g. 1.7.2) still reads that attribute inside predict_proba()
    and decision_function(), so a model trained on 1.9.0 and loaded
    on 1.7.2 raises:

        AttributeError: 'LogisticRegression' object has no
        attribute 'multi_class'

    Parameters
    ----------
    estimator:
        A fitted sklearn estimator, possibly missing version-specific
        attributes.

    Returns
    -------
    Any
        The same estimator, patched in place if needed.
    """

    if (
        type(estimator).__name__ == "LogisticRegression"
        and not hasattr(estimator, "multi_class")
    ):
        estimator.multi_class = "auto"

    return estimator


# ---------------------------------------------------------
# 2. Pipeline unwrapping helpers
# ---------------------------------------------------------

def _final_estimator(
    model: Any,
) -> Any:
    """
    Return the actual classifier inside a model object.

    Parameters
    ----------
    model:
        Either a bare sklearn/xgboost estimator, or a sklearn
        Pipeline ending in a classifier.

    Returns
    -------
    Any
        The final classifier, version-patched if necessary.
    """

    if isinstance(model, Pipeline):
        return _patch_version_gaps(model.steps[-1][1])

    return _patch_version_gaps(model)


def _split_pipeline(
    model: Any,
) -> Tuple[Optional[Pipeline], Any]:
    """
    Split a model into its preprocessing stage and final estimator.

    Parameters
    ----------
    model:
        Either a bare estimator or a multi-step sklearn Pipeline.

    Returns
    -------
    tuple
        (preprocessor, final_estimator). preprocessor is None when
        the model is not a multi-step Pipeline.
    """

    if isinstance(model, Pipeline) and len(model.steps) > 1:

        preprocessor = Pipeline(model.steps[:-1])
        final_estimator = model.steps[-1][1]

        return preprocessor, final_estimator

    return None, _final_estimator(model)


def _transform(
    preprocessor: Optional[Pipeline],
    X: pd.DataFrame,
) -> np.ndarray:
    """
    Apply the preprocessing pipeline, densifying sparse output.

    Parameters
    ----------
    preprocessor:
        Fitted preprocessing Pipeline, or None.

    X:
        Raw feature rows.

    Returns
    -------
    np.ndarray
        Transformed features, or X unchanged if preprocessor is None.
    """

    if preprocessor is None:
        return X

    X_transformed = preprocessor.transform(X)

    if hasattr(X_transformed, "toarray"):
        X_transformed = X_transformed.toarray()

    return X_transformed


def _transformed_feature_names(
    preprocessor: Optional[Pipeline],
    fallback_names: List[str],
) -> List[str]:
    """
    Recover feature names after a ColumnTransformer, when possible.

    Parameters
    ----------
    preprocessor:
        Fitted preprocessing Pipeline, or None.

    fallback_names:
        Names to use if the preprocessor cannot report its own.

    Returns
    -------
    list
        Feature names matching the transformed feature space.
    """

    try:
        return list(preprocessor.get_feature_names_out())

    except Exception:
        return fallback_names


# ---------------------------------------------------------
# 3. Model type detection
# ---------------------------------------------------------

def detect_model_type(
    model: Any,
) -> str:
    """
    Identify the model family so the correct SHAP explainer can
    be selected.

    Parameters
    ----------
    model:
        Either a bare estimator or a sklearn Pipeline. Pipelines are
        unwrapped so the final classifier is inspected directly.

    Returns
    -------
    str
        One of "logistic_regression", "random_forest", "xgboost",
        "gradient_boosting", "svm", or "unknown".
    """

    estimator = _final_estimator(model)

    module_name = type(estimator).__module__.lower()
    class_name = type(estimator).__name__.lower()

    if "logisticregression" in class_name:
        return "logistic_regression"

    if "randomforest" in class_name:
        return "random_forest"

    if "xgb" in module_name or "xgb" in class_name:
        return "xgboost"

    if (
        "gradientboosting" in class_name
        or "lgbm" in class_name
        or "lightgbm" in module_name
    ):
        return "gradient_boosting"

    if "svc" in class_name or "svm" in module_name:
        return "svm"

    return "unknown"


# ---------------------------------------------------------
# 4. Manual linear explainer (fallback for logistic regression)
# ---------------------------------------------------------

class _ManualLinearExplainer:
    """
    Version-safe replacement for shap.LinearExplainer, used only
    for binary logistic regression.

    shap.LinearExplainer internally reads a ``model.multi_class``
    attribute in some code paths (notably single-row calls). Newer
    sklearn training environments no longer set that attribute the
    way older shap releases expect. SHAP values for a linear model
    have a known closed form under the standard independent-features
    assumption:

        phi_i = coef_i * (x_i - background_mean_i)

    Computing it directly avoids the version mismatch entirely.
    """

    def __init__(
        self,
        estimator: Any,
        background: np.ndarray,
    ) -> None:

        self.coef = np.asarray(
            estimator.coef_
        ).flatten()

        self.background_mean = np.asarray(
            background
        ).mean(axis=0)

    def shap_values(
        self,
        X: np.ndarray,
    ) -> np.ndarray:

        X = np.asarray(X)

        return (X - self.background_mean) * self.coef


# ---------------------------------------------------------
# 5. Explainer factory
# ---------------------------------------------------------

def get_explainer(
    model: Any,
    X_background: pd.DataFrame,
    model_type: Optional[str] = None,
) -> Tuple[Any, str, Optional[Pipeline], List[str]]:
    """
    Build a SHAP-compatible explainer matched to the model's type.

    Parameters
    ----------
    model:
        Bare estimator or sklearn Pipeline.

    X_background:
        Reference sample used as the background distribution for
        linear/kernel explainers.

    model_type:
        Pre-computed model type, to avoid re-detecting it.

    Returns
    -------
    tuple
        (explainer, model_type, preprocessor, feature_names_out).
    """

    if model_type is None:
        model_type = detect_model_type(model)

    preprocessor, final_estimator = _split_pipeline(model)

    X_background_transformed = _transform(
        preprocessor,
        X_background,
    )

    feature_names_out = (
        _transformed_feature_names(
            preprocessor,
            list(X_background.columns),
        )
        if preprocessor is not None
        else list(X_background.columns)
    )

    if model_type in (
        "random_forest",
        "xgboost",
        "gradient_boosting",
    ):

        explainer = shap.TreeExplainer(
            final_estimator
        )

    elif model_type == "logistic_regression":

        explainer = _ManualLinearExplainer(
            final_estimator,
            X_background_transformed,
        )

    else:

        background = shap.sample(
            X_background_transformed,
            min(50, len(X_background_transformed)),
        )

        predict_fn = lambda X: final_estimator.predict_proba(X)[:, 1]

        explainer = shap.KernelExplainer(
            predict_fn,
            background,
        )

    return explainer, model_type, preprocessor, feature_names_out


# ---------------------------------------------------------
# 6. SHAP value normalization
# ---------------------------------------------------------

def _shap_values_for_positive_class(
    explainer: Any,
    X: np.ndarray,
    model_type: str,
) -> np.ndarray:
    """
    Normalize SHAP output shape across explainer types.

    Parameters
    ----------
    explainer:
        A fitted SHAP-compatible explainer.

    X:
        Transformed feature rows to explain.

    model_type:
        The detected model family, currently unused but kept for
        future explainer-specific handling.

    Returns
    -------
    np.ndarray
        Contribution values toward the positive class (label 1).
    """

    raw = explainer.shap_values(X)

    if isinstance(raw, list):
        values = raw[1] if len(raw) > 1 else raw[0]
    else:
        values = raw

    values = np.asarray(values)

    if values.ndim == 3:
        values = values[:, :, 1]

    return values


# ---------------------------------------------------------
# 7. Global explanation
# ---------------------------------------------------------

def explain_global(
    model: Any,
    X_test: pd.DataFrame,
    feature_names: Optional[List[str]] = None,
    model_type: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Compute global feature importance across a test set.

    Parameters
    ----------
    model:
        Bare estimator or sklearn Pipeline.

    X_test:
        Feature rows to explain.

    feature_names:
        Optional override for output feature names.

    model_type:
        Pre-computed model type, to avoid re-detecting it.

    Returns
    -------
    dict
        JSON-serializable dictionary containing global SHAP
        feature importances, sorted descending.
    """

    try:

        explainer, model_type, preprocessor, feature_names_out = get_explainer(
            model,
            X_test,
            model_type,
        )

        names = (
            feature_names
            if feature_names is not None
            else feature_names_out
        )

        X_transformed = _transform(
            preprocessor,
            X_test,
        )

        shap_values = _shap_values_for_positive_class(
            explainer,
            X_transformed,
            model_type,
        )

        mean_abs = np.abs(shap_values).mean(axis=0)

        ranked = sorted(
            (
                {
                    "feature": feature,
                    "importance": float(value),
                }
                for feature, value in zip(names, mean_abs)
            ),
            key=lambda item: item["importance"],
            reverse=True,
        )

        return {
            "status": "PASS",
            "model_type": model_type,
            "global_features": ranked,
        }

    except Exception as error:

        return {
            "status": "ERROR",
            "model_type": model_type or detect_model_type(model),
            "global_features": [],
            "error": str(error),
        }


# ---------------------------------------------------------
# 8. Local explanation
# ---------------------------------------------------------

def explain_local(
    model: Any,
    X_test: pd.DataFrame,
    row_index: int,
    feature_names: Optional[List[str]] = None,
    model_type: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Compute a single-prediction SHAP explanation.

    Parameters
    ----------
    model:
        Bare estimator or sklearn Pipeline.

    X_test:
        Feature rows to explain.

    row_index:
        Positional index of the row in X_test to explain.

    feature_names:
        Optional override for output feature names.

    model_type:
        Pre-computed model type, to avoid re-detecting it.

    Returns
    -------
    dict
        JSON-serializable dictionary containing the predicted
        probability and per-feature contributions, sorted by
        absolute contribution descending.
    """

    try:

        row = X_test.iloc[[row_index]]

        explainer, model_type, preprocessor, feature_names_out = get_explainer(
            model,
            X_test,
            model_type,
        )

        names = (
            feature_names
            if feature_names is not None
            else feature_names_out
        )

        row_transformed = _transform(
            preprocessor,
            row,
        )

        shap_values = _shap_values_for_positive_class(
            explainer,
            row_transformed,
            model_type,
        )[0]

        row_values = np.asarray(row_transformed).flatten()

        explanation = [
            {
                "feature": feature,
                "value": (
                    float(value)
                    if pd.notna(value)
                    else None
                ),
                "contribution": float(contribution),
            }
            for feature, value, contribution in zip(
                names,
                row_values,
                shap_values,
            )
        ]

        explanation.sort(
            key=lambda item: abs(item["contribution"]),
            reverse=True,
        )

        predicted_probability = float(
            model.predict_proba(row)[0][1]
        )

        return {
            "status": "PASS",
            "model_type": model_type,
            "row_index": row_index,
            "predicted_probability": predicted_probability,
            "local_explanation": explanation,
        }

    except Exception as error:

        return {
            "status": "ERROR",
            "model_type": model_type or detect_model_type(model),
            "row_index": row_index,
            "local_explanation": [],
            "error": str(error),
        }


# ---------------------------------------------------------
# 9. Manual smoke test
# ---------------------------------------------------------

if __name__ == "__main__":

    import joblib

    MODEL_PATH = r"D:\sih26\SIH-2026\demo-models\biased_model_02.pkl"
    TEST_CSV = r"D:\sih26\SIH-2026\demo-assets\test_02.csv"
    TARGET_COL = "approved"

    model = joblib.load(MODEL_PATH)

    df = pd.read_csv(TEST_CSV)
    X_test = df.drop(columns=[TARGET_COL])

    print("Detected model type:", detect_model_type(model))

    global_result = explain_global(model, X_test)

    print("\n--- GLOBAL ---")

    if global_result["status"] == "ERROR":
        print("ERROR:", global_result["error"])
    else:
        for item in global_result["global_features"][:5]:
            print(f"{item['feature']:>25}: {item['importance']:.4f}")

    local_result = explain_local(model, X_test, row_index=0)

    print("\n--- LOCAL (row 0) ---")

    if local_result["status"] == "ERROR":
        print("ERROR:", local_result["error"])
    else:
        print(
            "Predicted probability of approval:",
            local_result["predicted_probability"],
        )
        for item in local_result["local_explanation"][:5]:
            print(
                f"{item['feature']:>25}: "
                f"value={item['value']}  "
                f"contribution={item['contribution']:.4f}"
            )