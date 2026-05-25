from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException

from pydantic import BaseModel
from datetime import datetime
import threading

from backend.auth.dependencies import (
    get_current_user
)

from backend.services.indexing_service import (
    IndexingService
)

import backend.app_state as app_state


router = APIRouter()


class IndexRequest(BaseModel):

    count: int
    bucket_name: str | None = None


# =========================================
# START INDEXING (non-blocking)
# =========================================

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

    # -----------------------------
    # CHECK IF ALREADY RUNNING
    # -----------------------------

    if app_state.sync_in_progress:

        return {
            "success": False,
            "message": "Sync already in progress",
            "sync_job": app_state.sync_job
        }

    # -----------------------------
    # DETERMINE BUCKET
    # -----------------------------

    bucket_name = request.bucket_name

    if not bucket_name:
        from backend.routes.bucket_routes import (
            get_active_bucket_name
        )
        bucket_name = get_active_bucket_name()

    # -----------------------------
    # INIT SYNC JOB STATE
    # -----------------------------

    app_state.sync_in_progress = True

    app_state.sync_job = {
        "status": "starting",
        "bucket": bucket_name,
        "batch_size": request.count,
        "processed": 0,
        "skipped": 0,
        "total_files": None,
        "remaining": None,
        "started_at": datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        ),
        "completed_at": None,
        "error": None,
        "message": None
    }

    # -----------------------------
    # START BACKGROUND THREAD
    # -----------------------------

    service = IndexingService()

    thread = threading.Thread(
        target=service.run_indexing,
        args=(request.count, bucket_name),
        daemon=True
    )

    thread.start()

    return {
        "success": True,
        "message": "Indexing started in background",
        "sync_job": app_state.sync_job
    }


# =========================================
# SYNC STATUS (poll this after starting)
# =========================================

@router.get("/sync-status")
async def sync_status(
    current_user=Depends(get_current_user)
):

    if current_user["role"] != "admin":

        raise HTTPException(
            status_code=403,
            detail="Admin only"
        )

    return {
        "success": True,
        "in_progress": app_state.sync_in_progress,
        "sync_job": app_state.sync_job
    }


# =========================================
# SYNC LOGS (per-bucket stats)
# =========================================

@router.get("/sync-logs")
async def sync_logs(
    current_user=Depends(get_current_user)
):

    if current_user["role"] != "admin":

        raise HTTPException(
            status_code=403,
            detail="Admin only"
        )

    service = IndexingService()
    logs = service.get_sync_logs()

    return {
        "success": True,
        "logs": logs
    }