import warnings

warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
import pytest

from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from governance_engine.explainability import (
    detect_model_type,
    explain_global,
    explain_local,
)


# ---------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------

@pytest.fixture
def sample_features():

    rng = np.random.RandomState(0)

    n_rows = 40

    data = pd.DataFrame(
        {
            "credit_score": rng.normal(650, 40, n_rows),
            "income": rng.normal(50000, 8000, n_rows),
            "region": rng.choice(
                ["North", "South"],
                size=n_rows,
            ),
        }
    )

    labels = (
        data["credit_score"] > 650
    ).astype(int)

    return data, labels


@pytest.fixture
def logistic_pipeline_model(sample_features):

    X, y = sample_features

    preprocessor = ColumnTransformer(
        transformers=[
            (
                "num",
                StandardScaler(),
                ["credit_score", "income"],
            ),
            (
                "cat",
                OneHotEncoder(handle_unknown="ignore"),
                ["region"],
            ),
        ]
    )

    model = Pipeline(
        steps=[
            ("preprocessing", preprocessor),
            ("classifier", LogisticRegression()),
        ]
    )

    model.fit(X, y)

    return model, X


@pytest.fixture
def random_forest_model(sample_features):

    X, y = sample_features
    X_numeric = X[["credit_score", "income"]]

    model = RandomForestClassifier(
        n_estimators=20,
        random_state=0,
    )

    model.fit(X_numeric, y)

    return model, X_numeric


# ---------------------------------------------------------
# Model type detection
# ---------------------------------------------------------

def test_detect_model_type_logistic_regression_pipeline(
    logistic_pipeline_model,
):

    model, _ = logistic_pipeline_model

    assert detect_model_type(
        model
    ) == "logistic_regression"


def test_detect_model_type_random_forest(
    random_forest_model,
):

    model, _ = random_forest_model

    assert detect_model_type(
        model
    ) == "random_forest"


def test_detect_model_type_bare_logistic_regression(
    sample_features,
):

    X, y = sample_features
    X_numeric = X[["credit_score", "income"]]

    model = LogisticRegression()
    model.fit(X_numeric, y)

    assert detect_model_type(
        model
    ) == "logistic_regression"


# ---------------------------------------------------------
# Global explanation
# ---------------------------------------------------------

def test_explain_global_returns_sorted_features(
    logistic_pipeline_model,
):

    model, X = logistic_pipeline_model

    result = explain_global(
        model=model,
        X_test=X,
    )

    assert result["status"] == "PASS"
    assert result["model_type"] == "logistic_regression"

    importances = [
        item["importance"]
        for item in result["global_features"]
    ]

    assert importances == sorted(
        importances,
        reverse=True,
    )

    assert len(result["global_features"]) > 0


def test_explain_global_random_forest(
    random_forest_model,
):

    model, X = random_forest_model

    result = explain_global(
        model=model,
        X_test=X,
    )

    assert result["status"] == "PASS"
    assert result["model_type"] == "random_forest"

    feature_names = [
        item["feature"]
        for item in result["global_features"]
    ]

    assert set(feature_names) == set(X.columns)


# ---------------------------------------------------------
# Local explanation
# ---------------------------------------------------------

def test_explain_local_returns_probability_and_contributions(
    logistic_pipeline_model,
):

    model, X = logistic_pipeline_model

    result = explain_local(
        model=model,
        X_test=X,
        row_index=0,
    )

    assert result["status"] == "PASS"
    assert result["row_index"] == 0

    assert 0.0 <= result[
        "predicted_probability"
    ] <= 1.0

    contributions = [
        abs(item["contribution"])
        for item in result["local_explanation"]
    ]

    assert contributions == sorted(
        contributions,
        reverse=True,
    )


def test_explain_local_contribution_values_are_json_safe(
    logistic_pipeline_model,
):

    model, X = logistic_pipeline_model

    result = explain_local(
        model=model,
        X_test=X,
        row_index=0,
    )

    for item in result["local_explanation"]:

        assert isinstance(
            item["contribution"],
            float,
        )

        assert (
            item["value"] is None
            or isinstance(item["value"], float)
        )


def test_explain_local_invalid_row_index_returns_error(
    logistic_pipeline_model,
):

    model, X = logistic_pipeline_model

    result = explain_local(
        model=model,
        X_test=X,
        row_index=9999,
    )

    assert result["status"] == "ERROR"
    assert "error" in result
    assert result["local_explanation"] == []