import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.mark.asyncio
async def test_health_check():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "StatFlow API"


@pytest.mark.asyncio
async def test_list_datasets_returns_list(monkeypatch):
    import app.routers.data as data_router

    async def mock_get_all():
        return []

    monkeypatch.setattr(data_router, "get_all_datasets", mock_get_all)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/data/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
