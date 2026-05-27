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

from backend.database import SessionLocal
from backend.models import Bucket, IndexingState


load_dotenv()

router = APIRouter()


# =========================================
# HELPERS
# =========================================

def _get_db():
    return SessionLocal()


def get_active_bucket_name():
    """Get the name of the currently active bucket."""

    db = _get_db()

    try:
        bucket = db.query(Bucket).filter(
            Bucket.is_active == True
        ).first()

        if bucket:
            return bucket.bucket_name

        # If no active bucket, ensure default exists
        default_bucket = os.getenv(
            "B2_BUCKET_NAME", "icf-bucket"
        )

        existing = db.query(Bucket).filter(
            Bucket.bucket_name == default_bucket
        ).first()

        if not existing:
            new_bucket = Bucket(
                bucket_name=default_bucket,
                is_active=True,
                created_by="system"
            )
            db.add(new_bucket)
            db.commit()

        return default_bucket

    finally:
        db.close()


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

    db = _get_db()

    try:
        buckets = db.query(Bucket).all()

        enriched = []

        for b in buckets:

            # Get indexing state for this bucket
            idx_state = db.query(IndexingState).filter(
                IndexingState.bucket_name == b.bucket_name
            ).first()

            total_files = (
                idx_state.total_files if idx_state else None
            )
            last_indexed = (
                idx_state.last_indexed if idx_state else 0
            )

            enriched.append({
                "bucket_name": b.bucket_name,
                "is_active": b.is_active,
                "created_at": (
                    b.created_at.strftime("%Y-%m-%d %H:%M:%S")
                    if b.created_at else None
                ),
                "created_by": b.created_by,
                "total_synced": last_indexed,
                "total_files": total_files,
                "remaining": (
                    max(0, total_files - last_indexed)
                    if total_files is not None
                    else None
                ),
                "last_sync_date": (
                    idx_state.last_sync_date.strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )
                    if idx_state and idx_state.last_sync_date
                    else None
                )
            })

        return {
            "success": True,
            "buckets": enriched
        }

    finally:
        db.close()


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

    db = _get_db()

    try:
        # Check duplicate
        existing = db.query(Bucket).filter(
            Bucket.bucket_name == request.bucket_name
        ).first()

        if existing:
            raise HTTPException(
                status_code=400,
                detail="Bucket already registered"
            )

        new_bucket = Bucket(
            bucket_name=request.bucket_name,
            is_active=False,
            created_by=current_user["username"]
        )

        db.add(new_bucket)
        db.commit()

        return {
            "success": True,
            "message": (
                f"Bucket '{request.bucket_name}' added. "
                f"Use /set-active-bucket to activate it."
            )
        }

    except HTTPException:
        raise

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


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

    db = _get_db()

    try:
        # Find the target bucket
        target = db.query(Bucket).filter(
            Bucket.bucket_name == request.bucket_name
        ).first()

        if not target:
            raise HTTPException(
                status_code=404,
                detail="Bucket not found"
            )

        # Deactivate all buckets
        db.query(Bucket).update(
            {Bucket.is_active: False}
        )

        # Activate the target
        target.is_active = True
        db.commit()

        return {
            "success": True,
            "message": (
                f"Active bucket set to "
                f"'{request.bucket_name}'"
            )
        }

    except HTTPException:
        raise

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


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
