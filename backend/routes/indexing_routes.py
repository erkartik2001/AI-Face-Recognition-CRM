from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException

from pydantic import BaseModel
from typing import Optional
import httpx

from backend.auth.dependencies import (
    get_current_user
)

import backend.app_state as app_state


router = APIRouter()


# =========================================
# SCHEDULER ENDPOINTS (proxy to pipeline)
# =========================================

class SchedulerStartRequest(BaseModel):
    batch_size: Optional[int] = None
    interval_seconds: Optional[int] = None


@router.post("/scheduler/start")
async def scheduler_start(
    request: SchedulerStartRequest = SchedulerStartRequest(),
    current_user=Depends(get_current_user)
):
    """
    Start the automated indexing scheduler.
    Proxied to the Pipeline service.
    """

    if current_user["role"] != "admin":
        raise HTTPException(
            status_code=403, detail="Admin only"
        )

    try:
        async with httpx.AsyncClient() as client:
            body = {}
            if request.batch_size is not None:
                body["batch_size"] = request.batch_size
            if request.interval_seconds is not None:
                body["interval_seconds"] = (
                    request.interval_seconds
                )

            resp = await client.post(
                f"{app_state.pipeline_url}/scheduler/start",
                json=body,
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


@router.post("/scheduler/stop")
async def scheduler_stop(
    current_user=Depends(get_current_user)
):
    """
    Stop the automated indexing scheduler.
    """

    if current_user["role"] != "admin":
        raise HTTPException(
            status_code=403, detail="Admin only"
        )

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{app_state.pipeline_url}/scheduler/stop",
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


@router.get("/scheduler/status")
async def scheduler_status(
    current_user=Depends(get_current_user)
):
    """
    Get current scheduler status + live batch info.
    """

    if current_user["role"] != "admin":
        raise HTTPException(
            status_code=403, detail="Admin only"
        )

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{app_state.pipeline_url}/scheduler/status",
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


@router.get("/scheduler/logs")
async def scheduler_logs(
    current_user=Depends(get_current_user)
):
    """
    Get recent scheduler batch logs.
    """

    if current_user["role"] != "admin":
        raise HTTPException(
            status_code=403, detail="Admin only"
        )

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{app_state.pipeline_url}/scheduler/logs",
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
# SYNC STATUS (live progress of current batch)
# =========================================

@router.get("/sync-status")
async def sync_status(
    current_user=Depends(get_current_user)
):
    """
    Poll live indexing progress (works with scheduler).
    """

    if current_user["role"] != "admin":
        raise HTTPException(
            status_code=403, detail="Admin only"
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
# SYNC LOGS (per-bucket indexing stats)
# =========================================

@router.get("/sync-logs")
async def sync_logs(
    current_user=Depends(get_current_user)
):
    """
    Get per-bucket sync statistics.
    """

    if current_user["role"] != "admin":
        raise HTTPException(
            status_code=403, detail="Admin only"
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