import os
import shutil

from fastapi import APIRouter
from fastapi import UploadFile
from fastapi import File

from backend.matcher import FaceMatcher
from backend.services.storage_service import B2Storage


router = APIRouter()

matcher = FaceMatcher()

storage = B2Storage()


UPLOAD_FOLDER = "uploads"

os.makedirs(
    UPLOAD_FOLDER,
    exist_ok=True
)


@router.post("/upload-face")
async def upload_face(
    file: UploadFile = File(...)
):

    try:

        # -----------------------------
        # SAVE TEMP FILE
        # -----------------------------

        temp_path = os.path.join(
            UPLOAD_FOLDER,
            file.filename
        )

        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(
                file.file,
                buffer
            )

        # -----------------------------
        # UPLOAD TO B2
        # -----------------------------

        upload_result = storage.upload_file(
            local_file_path=temp_path,
            b2_file_name=file.filename
        )

        file_url = upload_result["file_url"]

        # -----------------------------
        # GENERATE EMBEDDING
        # -----------------------------

        embedding = matcher.engine.get_embedding(
            temp_path
        )

        if embedding is None:

            return {
                "success": False,
                "message": "No face detected"
            }

        # -----------------------------
        # ADD TO FAISS
        # -----------------------------

        matcher.add_face(
            embedding=embedding,
            file_name=file.filename,
            file_url=file_url
        )

        # -----------------------------
        # REMOVE TEMP FILE
        # -----------------------------

        os.remove(temp_path)

        return {
            "success": True,
            "message": "Face uploaded successfully",
            "file_url": file_url
        }

    except Exception as e:

        return {
            "success": False,
            "error": str(e)
        }