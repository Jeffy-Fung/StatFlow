from pydantic import BaseModel, Field
from typing import Optional


class DatasetBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None


class DatasetCreate(DatasetBase):
    pass


class DatasetUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None


class DatasetResponse(DatasetBase):
    id: str = Field(..., alias="_id")
    owner: str
    created_at: str
    columns: Optional[list[str]] = None
    row_count: Optional[int] = None

    model_config = {"populate_by_name": True}
