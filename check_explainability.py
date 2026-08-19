"""
check_real_artifact.py

Verify explain_global() / explain_local() against a REAL trained
model and test CSV (not synthetic data).

Usage
-----
    python check_real_artifact.py

    python check_real_artifact.py \\
        --model-path demo-models/biased_model_02.pkl \\
        --test-csv demo-assets/test_02.csv \\
        --target-col approved

    python check_real_artifact.py --row-index 5
"""

import argparse
import os
import sys
import warnings

warnings.filterwarnings("ignore")

import joblib
import pandas as pd

from governance_engine.explainability import (
    detect_model_type,
    explain_global,
    explain_local,
)


# ---------------------------------------------------------
# 1. CLI arguments
# ---------------------------------------------------------

def parse_args():

    parser = argparse.ArgumentParser(
        description="Run explain_global()/explain_local() against a real model + test CSV.",
    )

    parser.add_argument(
        "--model-path",
        default=r"demo-models/biased_model_02.pkl",
        help="Path to the trained model .pkl file.",
    )

    parser.add_argument(
        "--test-csv",
        default=r"demo-assets/test_02.csv",
        help="Path to the test CSV file.",
    )

    parser.add_argument(
        "--target-col",
        default="approved",
        help="Name of the target/label column to drop before explaining.",
    )

    parser.add_argument(
        "--row-index",
        type=int,
        default=0,
        help="Row index to use for the local explanation.",
    )

    parser.add_argument(
        "--top-n",
        type=int,
        default=5,
        help="Number of top features to print for global/local results.",
    )

    return parser.parse_args()


# ---------------------------------------------------------
# 2. Loading + validation
# ---------------------------------------------------------

def load_model_and_data(model_path, test_csv, target_col):

    if not os.path.exists(model_path):
        print(f"FAIL: model file not found -> {model_path}")
        sys.exit(1)

    if not os.path.exists(test_csv):
        print(f"FAIL: test CSV not found -> {test_csv}")
        sys.exit(1)

    model = joblib.load(model_path)

    df = pd.read_csv(test_csv)

    if target_col not in df.columns:
        print(
            f"FAIL: target column '{target_col}' not found in {test_csv}. "
            f"Available columns: {list(df.columns)}"
        )
        sys.exit(1)

    X_test = df.drop(columns=[target_col])

    return model, X_test


# ---------------------------------------------------------
# 3. Global explanation check
# ---------------------------------------------------------

def run_global_check(model, X_test, top_n):

    print("\n--- GLOBAL ---")

    global_result = explain_global(model, X_test)

    if global_result["status"] == "ERROR":
        print("ERROR:", global_result["error"])
        return False

    for item in global_result["global_features"][:top_n]:
        print(f"{item['feature']:>25}: {item['importance']:.4f}")

    return True


# ---------------------------------------------------------
# 4. Local explanation check
# ---------------------------------------------------------

def run_local_check(model, X_test, row_index, top_n):

    print(f"\n--- LOCAL (row {row_index}) ---")

    local_result = explain_local(model, X_test, row_index=row_index)

    if local_result["status"] == "ERROR":
        print("ERROR:", local_result["error"])
        return False

    print(
        "Predicted probability of approval:",
        local_result["predicted_probability"],
    )

    for item in local_result["local_explanation"][:top_n]:
        print(
            f"{item['feature']:>25}: "
            f"value={item['value']}  "
            f"contribution={item['contribution']:.4f}"
        )

    return True


# ---------------------------------------------------------
# 5. Main
# ---------------------------------------------------------

if __name__ == "__main__":

    args = parse_args()

    model, X_test = load_model_and_data(
        args.model_path,
        args.test_csv,
        args.target_col,
    )

    print("Model path:", args.model_path)
    print("Test CSV:", args.test_csv)
    print("Detected model type:", detect_model_type(model))

    global_ok = run_global_check(model, X_test, args.top_n)
    local_ok = run_local_check(model, X_test, args.row_index, args.top_n)

    print()

    if global_ok and local_ok:
        print("PASS -- both global and local explanations ran successfully.")
        sys.exit(0)
    else:
        print("FAIL -- see errors above.")
        sys.exit(1)