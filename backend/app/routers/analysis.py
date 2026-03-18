from fastapi import APIRouter, Depends, HTTPException, status

from app.analysis import run_analysis
from app.auth import get_current_user
from app.models.dataset import get_dataset_by_id

router = APIRouter(prefix="/api/analysis", tags=["analysis"])


@router.post("/run/{dataset_id}", status_code=status.HTTP_200_OK)
async def run_analysis_on_dataset(
    dataset_id: str,
    current_user: dict = Depends(get_current_user),
):
    """Run all applicable statistical tests on an uploaded dataset.

    Currently detects and runs an independent t-test when the dataset
    contains exactly two numeric columns.  Additional tests will be
    added to the registry and executed automatically.
    """
    dataset = await get_dataset_by_id(dataset_id)
    if not dataset:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dataset not found")

    columns: list[str] = dataset.get("columns") or []
    rows: list[dict] = dataset.get("rows") or []

    if not columns:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Dataset has no columns",
        )

    results = run_analysis(columns, rows)

    return {
        "dataset_id": dataset_id,
        "columns": columns,
        "tests_run": len(results),
        "results": results,
    }
