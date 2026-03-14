from fastapi import APIRouter, Depends, HTTPException, status

from app.models.dataset import (
    create_dataset,
    delete_dataset,
    get_all_datasets,
    update_dataset,
)
from app.schemas.dataset import DatasetCreate, DatasetUpdate
from app.auth import get_current_user

router = APIRouter(prefix="/api/data", tags=["data"])


@router.get("/")
async def list_datasets():
    """Retrieve all datasets."""
    return await get_all_datasets()


@router.post("/", status_code=status.HTTP_201_CREATED)
async def add_dataset(
    payload: DatasetCreate,
    current_user: dict = Depends(get_current_user),
):
    """Add a new dataset. Requires authentication."""
    return await create_dataset(payload.model_dump(), owner=current_user["username"])


@router.put("/{dataset_id}")
async def modify_dataset(
    dataset_id: str,
    payload: DatasetUpdate,
    current_user: dict = Depends(get_current_user),
):
    """Update an existing dataset. Requires authentication."""
    updated = await update_dataset(dataset_id, payload.model_dump(exclude_none=True))
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dataset not found")
    return updated


@router.delete("/{dataset_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_dataset(
    dataset_id: str,
    current_user: dict = Depends(get_current_user),
):
    """Delete a specified dataset. Requires authentication."""
    deleted = await delete_dataset(dataset_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dataset not found")
