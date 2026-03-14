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

