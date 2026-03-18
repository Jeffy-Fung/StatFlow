from app.database import db
from bson import ObjectId
from bson.errors import InvalidId
from datetime import datetime, timezone
from pymongo import ReturnDocument


async def get_dataset_by_id(dataset_id: str) -> dict | None:
    try:
        oid = ObjectId(dataset_id)
    except InvalidId:
        return None
    doc = await db["datasets"].find_one({"_id": oid})
    if doc:
        doc["_id"] = str(doc["_id"])
        if isinstance(doc.get("created_at"), datetime):
            doc["created_at"] = doc["created_at"].isoformat()
    return doc


async def get_all_datasets() -> list[dict]:
    cursor = db["datasets"].find()
    datasets = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        if isinstance(doc.get("created_at"), datetime):
            doc["created_at"] = doc["created_at"].isoformat()
        datasets.append(doc)
    return datasets


async def create_dataset(payload: dict, owner: str) -> dict:
    payload["owner"] = owner
    payload["created_at"] = datetime.now(timezone.utc)
    result = await db["datasets"].insert_one(payload)
    payload["_id"] = str(result.inserted_id)
    payload["created_at"] = payload["created_at"].isoformat()
    return payload


async def update_dataset(dataset_id: str, payload: dict, owner: str) -> dict | None:
    try:
        oid = ObjectId(dataset_id)
    except InvalidId:
        return None
    result = await db["datasets"].find_one_and_update(
        {"_id": oid, "owner": owner},
        {"$set": payload},
        return_document=ReturnDocument.AFTER,
    )
    if result:
        result["_id"] = str(result["_id"])
    return result


async def delete_dataset(dataset_id: str, owner: str) -> bool:
    try:
        oid = ObjectId(dataset_id)
    except InvalidId:
        return False
    result = await db["datasets"].delete_one({"_id": oid, "owner": owner})
    return result.deleted_count == 1
