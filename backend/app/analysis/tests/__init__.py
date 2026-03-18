from app.analysis.tests import t_test

# Registry of all available statistical tests.
# Each module must expose:
#   applicable(columns, rows) -> bool
#   run(columns, rows) -> dict
ALL_TESTS = [t_test]
