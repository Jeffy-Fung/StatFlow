from app.database import db
from bson import ObjectId
from datetime import datetime, timezone


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


async def update_dataset(dataset_id: str, payload: dict) -> dict | None:
    result = await db["datasets"].find_one_and_update(
        {"_id": ObjectId(dataset_id)},
        {"$set": payload},
        return_document=True,
    )
    if result:
        result["_id"] = str(result["_id"])
    return result


async def delete_dataset(dataset_id: str) -> bool:
    result = await db["datasets"].delete_one({"_id": ObjectId(dataset_id)})
    return result.deleted_count == 1
