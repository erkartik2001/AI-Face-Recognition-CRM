from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
import threading
from pydantic import BaseModel
import time
import random

from backend.auth.dependencies import (
    get_current_user
)

from backend.services.indexing_service import (
    IndexingService
)


router = APIRouter()

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
    
    count = request.count

    service = IndexingService()
    
    response = service.start_indexing(batch_size=count)

    if count<=50:
        seconds = random.randint(80,90)

    else:
        seconds = random.randint(200, 400)

    time.sleep(seconds)

    return response