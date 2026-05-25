import json
import os
from datetime import datetime

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException

from pydantic import BaseModel
from dotenv import load_dotenv

from backend.auth.dependencies import (
    get_current_user
)


load_dotenv()

router = APIRouter()

BUCKETS_FILE = "backend/buckets.json"


# =========================================
# HELPERS
# =========================================

def load_buckets():
    """Load buckets. Auto-creates file on first access."""

    if not os.path.exists(BUCKETS_FILE):

        default_bucket = os.getenv(
            "B2_BUCKET_NAME", "icf-bucket"
        )

        buckets = [{
            "bucket_name": default_bucket,
            "is_active": True,
            "created_at": datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
            "created_by": "system"
        }]

        save_buckets(buckets)
        return buckets

    with open(BUCKETS_FILE, "r") as f:
        return json.load(f)


def save_buckets(buckets):

    with open(BUCKETS_FILE, "w") as f:
        json.dump(buckets, f, indent=4)


def get_active_bucket_name():
    """Get the name of the currently active bucket."""

    buckets = load_buckets()

    for b in buckets:
        if b.get("is_active"):
            return b["bucket_name"]

    return os.getenv("B2_BUCKET_NAME", "icf-bucket")


# =========================================
# MODELS
# =========================================

class AddBucketRequest(BaseModel):

    bucket_name: str


class SetActiveBucketRequest(BaseModel):

    bucket_name: str


# =========================================
# LIST BUCKETS (with sync stats)
# =========================================

@router.get("/buckets")
async def list_buckets(
    current_user=Depends(get_current_user)
):

    if current_user["role"] != "admin":

        raise HTTPException(
            status_code=403,
            detail="Admin only"
        )

    buckets = load_buckets()

    # Enrich with sync state
    from backend.services.indexing_service import (
        IndexingService
    )

    service = IndexingService()
    state = service.load_state()

    enriched = []

    for b in buckets:

        bucket_state = state.get(
            b["bucket_name"], {}
        )

        total_files = bucket_state.get("total_files")
        last_indexed = bucket_state.get(
            "last_indexed", 0
        )

        enriched.append({
            "bucket_name": b["bucket_name"],
            "is_active": b.get("is_active", False),
            "created_at": b.get("created_at"),
            "created_by": b.get("created_by"),
            "total_synced": last_indexed,
            "total_files": total_files,
            "remaining": (
                max(0, total_files - last_indexed)
                if total_files is not None
                else None
            ),
            "last_sync_date": bucket_state.get(
                "last_sync_date"
            )
        })

    return {
        "success": True,
        "buckets": enriched
    }


# =========================================
# ADD BUCKET
# =========================================

@router.post("/add-bucket")
async def add_bucket(
    request: AddBucketRequest,
    current_user=Depends(get_current_user)
):

    if current_user["role"] != "admin":

        raise HTTPException(
            status_code=403,
            detail="Admin only"
        )

    buckets = load_buckets()

    # Check duplicate
    for b in buckets:
        if b["bucket_name"] == request.bucket_name:
            raise HTTPException(
                status_code=400,
                detail="Bucket already registered"
            )

    buckets.append({
        "bucket_name": request.bucket_name,
        "is_active": False,
        "created_at": datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        ),
        "created_by": current_user["username"]
    })

    save_buckets(buckets)

    return {
        "success": True,
        "message": (
            f"Bucket '{request.bucket_name}' added. "
            f"Use /set-active-bucket to activate it."
        )
    }


# =========================================
# SET ACTIVE BUCKET
# =========================================

@router.post("/set-active-bucket")
async def set_active_bucket(
    request: SetActiveBucketRequest,
    current_user=Depends(get_current_user)
):

    if current_user["role"] != "admin":

        raise HTTPException(
            status_code=403,
            detail="Admin only"
        )

    buckets = load_buckets()

    found = False

    for b in buckets:
        if b["bucket_name"] == request.bucket_name:
            b["is_active"] = True
            found = True
        else:
            b["is_active"] = False

    if not found:
        raise HTTPException(
            status_code=404,
            detail="Bucket not found"
        )

    save_buckets(buckets)

    return {
        "success": True,
        "message": (
            f"Active bucket set to "
            f"'{request.bucket_name}'"
        )
    }


# =========================================
# GET ACTIVE BUCKET
# =========================================

@router.get("/active-bucket")
async def active_bucket(
    current_user=Depends(get_current_user)
):

    if current_user["role"] != "admin":

        raise HTTPException(
            status_code=403,
            detail="Admin only"
        )

    name = get_active_bucket_name()

    return {
        "success": True,
        "bucket_name": name
    }
