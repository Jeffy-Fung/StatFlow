"""Independent two-sample t-test.

Applicable when the dataset has exactly two columns that both contain
numeric (float-parseable) values.
"""

from __future__ import annotations

import statistics
from typing import Any


def applicable(columns: list[str], rows: list[dict]) -> bool:
    """Return True only when the dataset has exactly 2 numeric columns."""
    if len(columns) != 2:
        return False

    if not rows:
        return False

    # Inspect up to the first 10 rows to decide numeric eligibility.
    sample = rows[:10]
    for row in sample:
        for col in columns:
            try:
                float(row[col])
            except (ValueError, TypeError):
                return False
    return True


def run(columns: list[str], rows: list[dict]) -> dict[str, Any]:
    """Run an independent samples t-test on two columns.

    Returns a dict with the test name, per-column descriptive stats,
    the t-statistic, p-value, and a boolean *significant* flag
    (alpha = 0.05).
    """
    from scipy import stats  # deferred so scipy is only required when used

    col_a, col_b = columns

    try:
        group_a = [float(r[col_a]) for r in rows if r.get(col_a) is not None]
        group_b = [float(r[col_b]) for r in rows if r.get(col_b) is not None]
    except (ValueError, TypeError) as exc:
        raise ValueError(f"Non-numeric data found in columns: {exc}") from exc

    if len(group_a) < 2 or len(group_b) < 2:
        raise ValueError("Each column must have at least 2 values for t-test")

    result = stats.ttest_ind(group_a, group_b)

    return {
        "test": "independent_t_test",
        "column_a": col_a,
        "column_b": col_b,
        "n_a": len(group_a),
        "n_b": len(group_b),
        "mean_a": round(statistics.mean(group_a), 6),
        "mean_b": round(statistics.mean(group_b), 6),
        "t_statistic": round(float(result.statistic), 6),
        "p_value": round(float(result.pvalue), 6),
        "significant": bool(result.pvalue < 0.05),
    }
