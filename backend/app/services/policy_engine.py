from typing import Dict, Any, List, Tuple
from app.models.schemas import PolicyRule

DEFAULT_POLICIES: List[PolicyRule] = [
    PolicyRule(
        metric="fairness.demographic_parity_gap",
        operator="<=",
        threshold=0.15,
        severity="BLOCK"
    ),
    PolicyRule(
        metric="fairness.disparate_impact_ratio",
        operator=">=",
        threshold=0.80,
        severity="BLOCK"
    ),
    PolicyRule(
        metric="fairness.tpr_gap",
        operator="<=",
        threshold=0.10,
        severity="WARNING"
    ),
    PolicyRule(
        metric="performance.accuracy",
        operator=">=",
        threshold=0.75,
        severity="BLOCK"
    ),
]

def _get_nested_value(data: Dict[str, Any], path: str) -> Any:
    keys = path.split(".")
    val = data
    for k in keys:
        if isinstance(val, dict) and k in val:
            val = val[k]
        else:
            return None
    return val

def evaluate_policies(
    audit_data: Dict[str, Any], 
    rules: List[PolicyRule] = None
) -> Tuple[str, List[str]]:
    rules_to_apply = rules if rules is not None else DEFAULT_POLICIES
    reasons: List[str] = []
    has_block = False
    has_warning = False

    for rule in rules_to_apply:
        val = _get_nested_value(audit_data, rule.metric)
        if val is None:
            continue

        failed = False
        if rule.operator == "<=" and not (val <= rule.threshold):
            failed = True
        elif rule.operator == "<" and not (val < rule.threshold):
            failed = True
        elif rule.operator == ">=" and not (val >= rule.threshold):
            failed = True
        elif rule.operator == ">" and not (val > rule.threshold):
            failed = True
        elif rule.operator == "==" and not (val == rule.threshold):
            failed = True

        if failed:
            msg = (
                f"Policy violation ({rule.severity}): '{rule.metric}' value {val} "
                f"violated condition '{rule.operator} {rule.threshold}'"
            )
            reasons.append(msg)
            if rule.severity.upper() == "BLOCK":
                has_block = True
            elif rule.severity.upper() in ["WARNING", "REVIEW"]:
                has_warning = True

    if has_block:
        return "BLOCK", reasons
    elif has_warning:
        return "WARNING", reasons
    else:
        return "PASS", ["All organizational governance policies passed."]