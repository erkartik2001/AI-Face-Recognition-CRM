import os
import shutil

from fastapi import APIRouter, UploadFile, File

import backend.app_state as app_state
import httpx

router = APIRouter()


UPLOAD_FOLDER = "uploads"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@router.post("/search-face")
async def search_face(file: UploadFile = File(...)):
    """
    Proxy face search to the Pipeline service.
    Forwards the uploaded image and returns matches.
    """

    # Read the uploaded file content
    file_content = await file.read()

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{app_state.pipeline_url}/search-face",
                files={
                    "file": (
                        file.filename,
                        file_content,
                        file.content_type or "image/jpeg"
                    )
                },
                timeout=30.0
            )

            return resp.json()

    except httpx.TimeoutException:
        return {
            "success": False,
            "matches": [],
            "message": "Pipeline service timeout"
        }
    except Exception as e:
        return {
            "success": False,
            "matches": [],
            "message": f"Pipeline service error: {e}"
        }