"""Simple feature-drift detection for TrustLayer MVP."""

from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd
from scipy import stats


def detect_feature_drift(
    reference_df: pd.DataFrame,
    production_df: pd.DataFrame,
    feature_names: List[str],
    threshold: float = 0.15,
    exclude_columns: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Compare reference and production distributions using KS statistic.

    Returns JSON-serializable drift summary for the API contract.
    """
    excluded = set(exclude_columns or [])
    drift_features: List[Dict[str, Any]] = []
    drifted: List[str] = []

    for feature in feature_names:
        if feature in excluded:
            continue
        if feature not in reference_df.columns or feature not in production_df.columns:
            continue

        ref_series = reference_df[feature].dropna()
        prod_series = production_df[feature].dropna()

        if ref_series.empty or prod_series.empty:
            continue

        if pd.api.types.is_numeric_dtype(ref_series):
            score = float(stats.ks_2samp(ref_series, prod_series).statistic)
            method = "ks_statistic"
        else:
            ref_counts = ref_series.value_counts(normalize=True)
            prod_counts = prod_series.value_counts(normalize=True)
            categories = sorted(set(ref_counts.index) | set(prod_counts.index))
            ref_probs = np.array([ref_counts.get(cat, 0.0) for cat in categories])
            prod_probs = np.array([prod_counts.get(cat, 0.0) for cat in categories])
            score = float(0.5 * np.abs(ref_probs - prod_probs).sum())
            method = "l1_category_shift"

        detected = score >= threshold
        if detected:
            drifted.append(feature)

        drift_features.append(
            {
                "feature": feature,
                "drift_score": round(score, 3),
                "drift_detected": detected,
                "method": method,
            }
        )

    if not drift_features:
        return {"status": "NOT_RUN", "features": []}

    if drifted:
        status = "WARNING" if len(drifted) <= 2 else "FAIL"
    else:
        status = "PASS"

    return {
        "status": status,
        "features": drift_features,
        "drifted_features": drifted,
    }
