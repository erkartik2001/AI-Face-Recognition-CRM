import os
import shutil

from fastapi import APIRouter, UploadFile, File

import backend.app_state as app_state

router = APIRouter()


UPLOAD_FOLDER = "uploads"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@router.post("/search-face")
async def search_face(file: UploadFile = File(...)):

    # save uploaded file
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    #search matches
    results = app_state.matcher.search(file_path)

    return{
        "success" : True,
        "matches" : results
    }