"""Analysis runner.

Iterates through every registered test in ``ALL_TESTS``, runs each one
that declares itself applicable for the given dataset, and returns a list
of per-test result dicts.  Tests are executed in the order they appear in
the registry so they can later be arranged to run sequentially with
shared context if needed.
"""

from __future__ import annotations

from app.analysis.tests import ALL_TESTS


def run_analysis(columns: list[str], rows: list[dict]) -> list[dict]:
    """Run all applicable statistical tests and return their results.

    Each entry in the returned list is one of:
      * ``{"status": "success", "result": {...}}``
      * ``{"status": "error",   "test": "<name>", "message": "<reason>"}``
    """
    results: list[dict] = []
    for test_module in ALL_TESTS:
        if not test_module.applicable(columns, rows):
            continue
        try:
            result = test_module.run(columns, rows)
            results.append({"status": "success", "result": result})
        except Exception as exc:  # noqa: BLE001
            test_name = getattr(test_module, "__name__", str(test_module)).split(".")[-1]
            results.append({"status": "error", "test": test_name, "message": str(exc)})
    return results
