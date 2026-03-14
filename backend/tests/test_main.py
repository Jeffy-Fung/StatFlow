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
# Health check
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_health_check():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "StatFlow API"


# ---------------------------------------------------------------------------
# Dataset list (public)
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Register
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_register_happy_path(monkeypatch):
    import app.routers.auth as auth_router

    async def mock_get_user(username):
        return None

    async def mock_create_user(username, password):
        return {"_id": "abc123", "username": username}

    monkeypatch.setattr(auth_router, "get_user_by_username", mock_get_user)
    monkeypatch.setattr(auth_router, "create_user", mock_create_user)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/api/auth/register", json={"username": "alice", "password": "secret123"}
        )
    assert response.status_code == 201
    assert response.json()["username"] == "alice"


@pytest.mark.asyncio
async def test_register_duplicate_username(monkeypatch):
    import app.routers.auth as auth_router

    async def mock_get_user(username):
        return {"username": username}

    monkeypatch.setattr(auth_router, "get_user_by_username", mock_get_user)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/api/auth/register", json={"username": "alice", "password": "secret123"}
        )
    assert response.status_code == 400


# ---------------------------------------------------------------------------
# Login
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_login_happy_path(monkeypatch):
    import app.routers.auth as auth_router

    async def mock_authenticate(username, password):
        return {"username": username}

    monkeypatch.setattr(auth_router, "authenticate_user", mock_authenticate)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/api/auth/login",
            data={"username": "alice", "password": "secret123"},
        )
    assert response.status_code == 200
    body = response.json()
    assert "access_token" in body
    assert body["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_invalid_credentials(monkeypatch):
    import app.routers.auth as auth_router

    async def mock_authenticate(username, password):
        return None

    monkeypatch.setattr(auth_router, "authenticate_user", mock_authenticate)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/api/auth/login",
            data={"username": "alice", "password": "wrong"},
        )
    assert response.status_code == 401


# ---------------------------------------------------------------------------
# Protected routes — missing / invalid token
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_add_dataset_no_token():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/api/data/", json={"name": "ds", "description": "d"})
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_add_dataset_invalid_token():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/api/data/",
            json={"name": "ds", "description": "d"},
            headers={"Authorization": "Bearer bad.token.here"},
        )
    assert response.status_code == 401


# ---------------------------------------------------------------------------
# Ownership enforcement — update / delete
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_update_dataset_owner_succeeds(monkeypatch):
    import app.routers.data as data_router
    import app.auth as auth_module

    async def mock_get_user(username):
        return {"username": "alice"}

    async def mock_update(dataset_id, payload, owner):
        assert owner == "alice"
        return {"_id": dataset_id, "name": payload.get("name", "updated"), "owner": owner}

    monkeypatch.setattr(auth_module, "get_user_by_username", mock_get_user)
    monkeypatch.setattr(data_router, "update_dataset", mock_update)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.put(
            "/api/data/507f1f77bcf86cd799439011",
            json={"name": "renamed"},
            headers=_bearer("alice"),
        )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_update_dataset_non_owner_gets_404(monkeypatch):
    import app.routers.data as data_router
    import app.auth as auth_module

    async def mock_get_user(username):
        return {"username": "bob"}

    async def mock_update(dataset_id, payload, owner):
        # Owning filter not matched → return None
        return None

    monkeypatch.setattr(auth_module, "get_user_by_username", mock_get_user)
    monkeypatch.setattr(data_router, "update_dataset", mock_update)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.put(
            "/api/data/507f1f77bcf86cd799439011",
            json={"name": "renamed"},
            headers=_bearer("bob"),
        )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_dataset_owner_succeeds(monkeypatch):
    import app.routers.data as data_router
    import app.auth as auth_module

    async def mock_get_user(username):
        return {"username": "alice"}

    async def mock_delete(dataset_id, owner):
        assert owner == "alice"
        return True

    monkeypatch.setattr(auth_module, "get_user_by_username", mock_get_user)
    monkeypatch.setattr(data_router, "delete_dataset", mock_delete)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.delete(
            "/api/data/507f1f77bcf86cd799439011",
            headers=_bearer("alice"),
        )
    assert response.status_code == 204


@pytest.mark.asyncio
async def test_delete_dataset_non_owner_gets_404(monkeypatch):
    import app.routers.data as data_router
    import app.auth as auth_module

    async def mock_get_user(username):
        return {"username": "bob"}

    async def mock_delete(dataset_id, owner):
        # Owning filter not matched → nothing deleted
        return False

    monkeypatch.setattr(auth_module, "get_user_by_username", mock_get_user)
    monkeypatch.setattr(data_router, "delete_dataset", mock_delete)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.delete(
            "/api/data/507f1f77bcf86cd799439011",
            headers=_bearer("bob"),
        )
    assert response.status_code == 404

