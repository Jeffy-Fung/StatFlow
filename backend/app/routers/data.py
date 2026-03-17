import csv
import io
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, Response, UploadFile, status

from app.models.dataset import (
    create_dataset,
    delete_dataset,
    get_all_datasets,
    update_dataset,
)
from app.schemas.dataset import DatasetCreate, DatasetUpdate
from app.auth import get_current_user

router = APIRouter(prefix="/api/data", tags=["data"])

_MAX_UPLOAD_BYTES = 10 * 1024 * 1024  # 10 MB


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
    updated = await update_dataset(dataset_id, payload.model_dump(exclude_none=True), owner=current_user["username"])
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dataset not found")
    return updated


@router.delete("/{dataset_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_dataset(
    dataset_id: str,
    current_user: dict = Depends(get_current_user),
):
    """Delete a specified dataset. Requires authentication."""
    deleted = await delete_dataset(dataset_id, owner=current_user["username"])
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dataset not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_dataset(
    file: UploadFile = File(...),
    name: Annotated[str, Form(min_length=1, max_length=200)] = ...,
    description: Annotated[Optional[str], Form()] = None,
    current_user: dict = Depends(get_current_user),
):
    """Upload a CSV file as a new dataset. Requires authentication."""
    if not (file.filename or "").lower().endswith(".csv"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only CSV files are supported",
        )

    # Stream-read with an enforced cap to avoid loading oversized uploads into memory
    _CHUNK_SIZE = 64 * 1024  # 64 KB
    chunks: list[bytes] = []
    total = 0
    while True:
        chunk = await file.read(_CHUNK_SIZE)
        if not chunk:
            break
        total += len(chunk)
        if total > _MAX_UPLOAD_BYTES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File exceeds the 10 MB size limit",
            )
        chunks.append(chunk)
    raw = b"".join(chunks)

    # Use utf-8-sig to transparently strip the BOM that Excel adds to CSV exports
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be UTF-8 encoded",
        )

    # _EXTRA_KEY sentinel lets us detect rows that have more fields than the header
    _EXTRA_KEY = "__extra__"
    reader = csv.DictReader(io.StringIO(text), restkey=_EXTRA_KEY)
    columns = reader.fieldnames
    if not columns:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="CSV file must contain a header row",
        )

    # MongoDB rejects field names that start with '$' or contain '.'
    invalid = [c for c in columns if c.startswith("$") or "." in c]
    if invalid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid column name(s): {', '.join(invalid)}. "
                   "Column names must not start with '$' or contain '.'",
        )

    rows: list[dict] = []
    for i, row in enumerate(reader, start=2):
        if _EXTRA_KEY in row:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Row {i} has more fields than the header row",
            )
        rows.append(dict(row))

    payload = {
        "name": name,
        "description": description,
        "columns": list(columns),
        "row_count": len(rows),
        "rows": rows,
    }
    return await create_dataset(payload, owner=current_user["username"])
