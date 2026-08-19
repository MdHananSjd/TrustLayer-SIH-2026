"""
check_explainability.py

Quick sanity check -- run from the repo root:

    python check_explainability.py

Verifies:
  1. explainability.py imports cleanly and its functions run
  2. test_explainability.py passes under pytest
"""

import subprocess
import sys

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from governance_engine.explainability import (
    detect_model_type,
    explain_global,
    explain_local,
)


def check_explainability_module():

    print("1) Checking explainability.py functions run correctly...")

    rng = np.random.RandomState(0)
    X = pd.DataFrame({
        "credit_score": rng.normal(650, 40, 30),
        "income": rng.normal(50000, 8000, 30),
        "region": rng.choice(["North", "South"], size=30),
    })
    y = (X["credit_score"] > 650).astype(int)

    model = Pipeline([
        ("preprocessing", ColumnTransformer([
            ("num", StandardScaler(), ["credit_score", "income"]),
            ("cat", OneHotEncoder(handle_unknown="ignore"), ["region"]),
        ])),
        ("classifier", LogisticRegression()),
    ])
    model.fit(X, y)

    assert detect_model_type(model) == "logistic_regression"
    print("   - detect_model_type: OK")

    global_result = explain_global(model, X)
    assert global_result["status"] == "PASS"
    assert len(global_result["global_features"]) > 0
    print("   - explain_global: OK")

    local_result = explain_local(model, X, row_index=0)
    assert local_result["status"] == "PASS"
    assert 0.0 <= local_result["predicted_probability"] <= 1.0
    print("   - explain_local: OK")

    print("   PASS -- explainability.py works.\n")


def check_test_file():

    print("2) Running test_explainability.py under pytest...")

    result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/test_explainability.py", "-q"],
        capture_output=True,
        text=True,
    )

    print(result.stdout)

    if result.returncode == 0:
        print("   PASS -- test_explainability.py passes.\n")
    else:
        print("   FAIL -- see pytest output above.\n")
        print(result.stderr)

    return result.returncode == 0


if __name__ == "__main__":

    check_explainability_module()
    tests_ok = check_test_file()

    if tests_ok:
        print("ALL CHECKS PASSED.")
    else:
        print("SOME CHECKS FAILED -- see above.")
        sys.exit(1)