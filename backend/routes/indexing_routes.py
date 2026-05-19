from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException

from pydantic import BaseModel

from backend.auth.dependencies import (
    get_current_user
)

from backend.services.indexing_service import (
    IndexingService
)


router = APIRouter()

service = IndexingService()


class IndexRequest(BaseModel):

    count: int


@router.post("/start-indexing")
async def start_indexing(
    request: IndexRequest,
    current_user=Depends(get_current_user)
):

    # -----------------------------
    # ADMIN CHECK
    # -----------------------------

    if current_user["role"] != "admin":

        raise HTTPException(
            status_code=403,
            detail="Admin only"
        )

    result = service.start_indexing(
        batch_size=request.count
    )

    return result