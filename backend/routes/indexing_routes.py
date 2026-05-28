from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException

from pydantic import BaseModel
import httpx

from backend.auth.dependencies import (
    get_current_user
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
    """
    Proxy indexing request to the Pipeline service.
    Auth stays here in the CRM.
    """

    # -----------------------------
    # ADMIN CHECK
    # -----------------------------

    if current_user["role"] != "admin":

        raise HTTPException(
            status_code=403,
            detail="Admin only"
        )

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
    # CALL PIPELINE SERVICE
    # -----------------------------

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{app_state.pipeline_url}/start-indexing",
                json={
                    "count": request.count,
                    "bucket_name": bucket_name
                },
                timeout=10.0
            )

            return resp.json()

    except httpx.TimeoutException:
        raise HTTPException(
            status_code=504,
            detail="Pipeline service timeout"
        )
    except Exception as e:
        raise HTTPException(
            status_code=502,
            detail=f"Pipeline service error: {e}"
        )


# =========================================
# SYNC STATUS (poll this after starting)
# =========================================

@router.get("/sync-status")
async def sync_status(
    current_user=Depends(get_current_user)
):
    """
    Proxy sync status from the Pipeline service.
    """

    if current_user["role"] != "admin":

        raise HTTPException(
            status_code=403,
            detail="Admin only"
        )

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{app_state.pipeline_url}/sync-status",
                timeout=10.0
            )

            return resp.json()

    except httpx.TimeoutException:
        raise HTTPException(
            status_code=504,
            detail="Pipeline service timeout"
        )
    except Exception as e:
        raise HTTPException(
            status_code=502,
            detail=f"Pipeline service error: {e}"
        )


# =========================================
# SYNC LOGS (per-bucket stats)
# =========================================

@router.get("/sync-logs")
async def sync_logs(
    current_user=Depends(get_current_user)
):
    """
    Proxy sync logs from the Pipeline service.
    """

    if current_user["role"] != "admin":

        raise HTTPException(
            status_code=403,
            detail="Admin only"
        )

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{app_state.pipeline_url}/sync-logs",
                timeout=10.0
            )

            return resp.json()

    except httpx.TimeoutException:
        raise HTTPException(
            status_code=504,
            detail="Pipeline service timeout"
        )
    except Exception as e:
        raise HTTPException(
            status_code=502,
            detail=f"Pipeline service error: {e}"
        )