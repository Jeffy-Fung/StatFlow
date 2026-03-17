# StatFlow – Python Backend

## Tech Stack
| Layer | Technology |
|-------|-----------|
| Framework | [FastAPI](https://fastapi.tiangolo.com/) |
| Server | [Uvicorn](https://www.uvicorn.org/) (ASGI) |
| Database | [MongoDB](https://www.mongodb.com/) via [Motor](https://motor.readthedocs.io/) (async) |
| Auth | JWT ([python-jose](https://python-jose.readthedocs.io/)) + [passlib](https://passlib.readthedocs.io/) bcrypt |
| Validation | [Pydantic v2](https://docs.pydantic.dev/) |
| Testing | [pytest](https://pytest.org/) + [pytest-asyncio](https://pytest-asyncio.readthedocs.io/) |

## Project Structure
```
backend/
├── app/
│   ├── main.py          # FastAPI application entry point
│   ├── config.py        # Settings (loaded from .env)
│   ├── database.py      # MongoDB async client
│   ├── auth.py          # JWT helpers & OAuth2 dependency
│   ├── models/          # Database access layer
│   │   ├── dataset.py
│   │   └── user.py
│   ├── routers/         # API route handlers
│   │   ├── auth.py      # /api/auth/register, /api/auth/login
│   │   └── data.py      # /api/data CRUD
│   └── schemas/         # Pydantic request/response models
│       ├── dataset.py
│       └── user.py
├── tests/
│   └── test_main.py
├── .env.example
├── docker-compose.yml
├── Dockerfile
├── railway.toml
├── pyproject.toml
└── requirements.txt
```

## Quick Start

### Option A – Docker Compose (recommended)
```bash
# 1. Copy and edit the environment file
cp .env.example .env

# 2. Start the API and MongoDB together
docker compose up --build
```
The API is available at **http://localhost:8000**.

### Option B – Local Python
```bash
# 1. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Copy and edit the environment file
cp .env.example .env

# 4. Start MongoDB locally (or use Atlas), then run:
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Option C – Deploy to Railway

Railway builds from the `Dockerfile` and injects a `PORT` environment variable automatically.

1. **Create a new Railway project** and connect your GitHub repository.
2. **Set the root directory** to `backend` in the Railway service settings (or deploy from the repo root and Railway will pick up `backend/railway.toml`).
3. **Add a MongoDB service** from the Railway dashboard (*New → Database → MongoDB*). Railway will make the connection string available as a reference variable.
4. **Set the required environment variables** in the Railway service's *Variables* tab:

   | Variable | Value |
   |----------|-------|
   | `MONGODB_URL` | `${{MongoDB.MONGO_URL}}` (Railway reference variable) |
   | `DATABASE_NAME` | `statflow` |
   | `SECRET_KEY` | A long random string (e.g. `openssl rand -hex 32`) |
   | `ALGORITHM` | `HS256` |
   | `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` |
   | `ALLOWED_ORIGINS` | Your frontend URL, e.g. `https://your-app.up.railway.app` |

   > **Note:** `PORT` is set automatically by Railway — do **not** add it manually.

5. **Deploy.** Railway builds the image using `backend/Dockerfile` and starts the server using the Dockerfile's `CMD` (which reads `$PORT` automatically). The health check polls `/health`.

The deployed API will be available at the Railway-generated URL (e.g. `https://statflow-backend.up.railway.app`).

