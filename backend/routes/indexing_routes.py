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

    service = IndexingService()
    

    thread = threading.Thread(target=service.start_indexing)

    thread.start()

    seconds = random.randint(10, 35)

    time.sleep(seconds)

    return {
        "success": True,
        "message": "Indexing started"
    }