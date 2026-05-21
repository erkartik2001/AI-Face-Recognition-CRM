from fastapi import FastAPI

from backend.routes.search_routes import router as search_router
from backend.routes.auth_routes import router as auth_router
from backend.routes.indexing_routes import router as indexing_router
from backend.matcher import FaceMatcher
from contextlib import asynccontextmanager

from backend.app_state import matcher, face_engine, b2_storage
import backend.app_state as app_state

from backend.services.face_engine import FaceEngine
from backend.services.storage_service import B2Storage



@asynccontextmanager
async def lifespan(app: FastAPI):
   

    
    print("Loading Face Engine")
    app_state.face_engine = FaceEngine()
    print("Face Engine Loaded")
    print("-"*20)
    print("Loading B2 Storage")
    app_state.b2_storage = B2Storage()
    print("B2 Storage Loaded")
    print("-"*20)
    print("Loading Face Matcher....")
    app_state.matcher = FaceMatcher()
    print("Matcher loaded succesfully")


    yield

    print("Shutting down...")



app = FastAPI(
    title= "AI Face Recognition API", lifespan=lifespan
)

@app.get("/")
def home():

    return {
        "message" :  "AI Face Recognition API Running"
    }

# Register routes
app.include_router(search_router)
app.include_router(auth_router)
app.include_router(indexing_router)