from app.database import db
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def _hash(password: str) -> str:
    return pwd_context.hash(password)


def _verify(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


async def get_user_by_username(username: str) -> dict | None:
    return await db["users"].find_one({"username": username})


async def create_user(username: str, password: str) -> dict:
    hashed = _hash(password)
    doc = {"username": username, "hashed_password": hashed}
    result = await db["users"].insert_one(doc)
    doc["_id"] = str(result.inserted_id)
    return doc


async def authenticate_user(username: str, password: str) -> dict | None:
    user = await get_user_by_username(username)
    if not user or not _verify(password, user["hashed_password"]):
        return None
    return user
