"""Tests for the statistical analysis endpoint and analysis modules."""
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.auth import create_access_token


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _bearer(username: str) -> dict:
    token = create_access_token({"sub": username})
    return {"Authorization": f"Bearer {token}"}


# ---------------------------------------------------------------------------
# Unit tests — t_test module
# ---------------------------------------------------------------------------

from app.analysis.tests import t_test


class TestTTestApplicable:
    def _rows(self, cols, values_per_col):
        """Build rows list from parallel column value lists."""
        col_a, col_b = cols
        return [
            {col_a: str(a), col_b: str(b)}
            for a, b in zip(values_per_col[0], values_per_col[1])
        ]

    def test_exactly_two_numeric_columns_is_applicable(self):
        rows = self._rows(["a", "b"], [[1, 2, 3], [4, 5, 6]])
        assert t_test.applicable(["a", "b"], rows) is True

    def test_one_column_not_applicable(self):
        rows = [{"a": "1"}, {"a": "2"}]
        assert t_test.applicable(["a"], rows) is False

    def test_three_columns_not_applicable(self):
        rows = [{"a": "1", "b": "2", "c": "3"}]
        assert t_test.applicable(["a", "b", "c"], rows) is False

    def test_non_numeric_column_not_applicable(self):
        rows = [{"a": "hello", "b": "1"}, {"a": "world", "b": "2"}]
        assert t_test.applicable(["a", "b"], rows) is False

    def test_empty_rows_not_applicable(self):
        assert t_test.applicable(["a", "b"], []) is False


class TestTTestRun:
    def _rows(self, col_a, col_b, vals_a, vals_b):
        return [{col_a: str(a), col_b: str(b)} for a, b in zip(vals_a, vals_b)]

    def test_returns_expected_keys(self):
        rows = self._rows("x", "y", [1, 2, 3, 4, 5], [6, 7, 8, 9, 10])
        result = t_test.run(["x", "y"], rows)
        assert result["test"] == "independent_t_test"
        assert result["column_a"] == "x"
        assert result["column_b"] == "y"
        assert result["n_a"] == 5
        assert result["n_b"] == 5
        assert "t_statistic" in result
        assert "p_value" in result
        assert isinstance(result["significant"], bool)

    def test_identical_groups_not_significant(self):
        vals = [10.0, 20.0, 30.0, 40.0, 50.0]
        rows = self._rows("a", "b", vals, vals)
        result = t_test.run(["a", "b"], rows)
        assert result["significant"] is False

    def test_very_different_groups_significant(self):
        rows = self._rows("a", "b", [1, 2, 3, 4, 5], [100, 200, 300, 400, 500])
        result = t_test.run(["a", "b"], rows)
        assert result["significant"] is True

    def test_raises_on_non_numeric_data(self):
        rows = [{"a": "hello", "b": "1"}, {"a": "world", "b": "2"}]
        with pytest.raises(ValueError, match="Non-numeric"):
            t_test.run(["a", "b"], rows)

    def test_raises_when_too_few_values(self):
        rows = [{"a": "1", "b": "2"}]
        with pytest.raises(ValueError, match="at least 2"):
            t_test.run(["a", "b"], rows)


# ---------------------------------------------------------------------------
# Unit tests — runner
# ---------------------------------------------------------------------------

from app.analysis.runner import run_analysis


class TestRunner:
    def _rows(self, vals_a, vals_b):
        return [{"x": str(a), "y": str(b)} for a, b in zip(vals_a, vals_b)]

    def test_two_numeric_columns_produces_one_result(self):
        rows = self._rows([1, 2, 3, 4, 5], [6, 7, 8, 9, 10])
        results = run_analysis(["x", "y"], rows)
        assert len(results) == 1
        assert results[0]["status"] == "success"

    def test_single_column_produces_no_results(self):
        rows = [{"x": "1"}, {"x": "2"}, {"x": "3"}]
        results = run_analysis(["x"], rows)
        assert results == []

    def test_three_columns_produces_no_results(self):
        rows = [{"a": "1", "b": "2", "c": "3"}]
        results = run_analysis(["a", "b", "c"], rows)
        assert results == []

    def test_error_in_test_captured_gracefully(self, monkeypatch):
        import app.analysis.tests.t_test as _t_test

        monkeypatch.setattr(_t_test, "applicable", lambda cols, rows: True)
        monkeypatch.setattr(_t_test, "run", lambda cols, rows: (_ for _ in ()).throw(RuntimeError("boom")))

        rows = self._rows([1, 2], [3, 4])
        results = run_analysis(["x", "y"], rows)
        assert len(results) == 1
        assert results[0]["status"] == "error"
        assert "boom" in results[0]["message"]


# ---------------------------------------------------------------------------
# Integration tests — /api/analysis/run/{dataset_id} endpoint
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_run_analysis_no_token():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/api/analysis/run/507f1f77bcf86cd799439011")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_run_analysis_dataset_not_found(monkeypatch):
    import app.routers.analysis as analysis_router
    import app.auth as auth_module

    async def mock_get_user(username):
        return {"username": "alice"}

    async def mock_get_dataset(dataset_id):
        return None

    monkeypatch.setattr(auth_module, "get_user_by_username", mock_get_user)
    monkeypatch.setattr(analysis_router, "get_dataset_by_id", mock_get_dataset)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/api/analysis/run/507f1f77bcf86cd799439011",
            headers=_bearer("alice"),
        )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_run_analysis_two_numeric_columns(monkeypatch):
    import app.routers.analysis as analysis_router
    import app.auth as auth_module

    async def mock_get_user(username):
        return {"username": "alice"}

    async def mock_get_dataset(dataset_id):
        return {
            "_id": dataset_id,
            "columns": ["group_a", "group_b"],
            "rows": [
                {"group_a": str(v), "group_b": str(v + 100)}
                for v in range(1, 11)
            ],
        }

    monkeypatch.setattr(auth_module, "get_user_by_username", mock_get_user)
    monkeypatch.setattr(analysis_router, "get_dataset_by_id", mock_get_dataset)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/api/analysis/run/507f1f77bcf86cd799439011",
            headers=_bearer("alice"),
        )
    assert response.status_code == 200
    body = response.json()
    assert body["tests_run"] == 1
    assert body["results"][0]["status"] == "success"
    result = body["results"][0]["result"]
    assert result["test"] == "independent_t_test"
    assert result["column_a"] == "group_a"
    assert result["column_b"] == "group_b"
    assert result["significant"] is True


@pytest.mark.asyncio
async def test_run_analysis_single_column_no_tests(monkeypatch):
    import app.routers.analysis as analysis_router
    import app.auth as auth_module

    async def mock_get_user(username):
        return {"username": "alice"}

    async def mock_get_dataset(dataset_id):
        return {
            "_id": dataset_id,
            "columns": ["only_column"],
            "rows": [{"only_column": "1"}, {"only_column": "2"}],
        }

    monkeypatch.setattr(auth_module, "get_user_by_username", mock_get_user)
    monkeypatch.setattr(analysis_router, "get_dataset_by_id", mock_get_dataset)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/api/analysis/run/507f1f77bcf86cd799439011",
            headers=_bearer("alice"),
        )
    assert response.status_code == 200
    body = response.json()
    assert body["tests_run"] == 0
    assert body["results"] == []


@pytest.mark.asyncio
async def test_run_analysis_dataset_no_columns(monkeypatch):
    import app.routers.analysis as analysis_router
    import app.auth as auth_module

    async def mock_get_user(username):
        return {"username": "alice"}

    async def mock_get_dataset(dataset_id):
        return {"_id": dataset_id, "columns": [], "rows": []}

    monkeypatch.setattr(auth_module, "get_user_by_username", mock_get_user)
    monkeypatch.setattr(analysis_router, "get_dataset_by_id", mock_get_dataset)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/api/analysis/run/507f1f77bcf86cd799439011",
            headers=_bearer("alice"),
        )
    assert response.status_code == 400
