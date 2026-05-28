from fastapi import FastAPI

from backend.routes.search_routes import router as search_router
from backend.routes.auth_routes import router as auth_router
from backend.routes.indexing_routes import router as indexing_router
from backend.routes.bucket_routes import router as bucket_router
from contextlib import asynccontextmanager

import backend.app_state as app_state

from fastapi.middleware.cors import CORSMiddleware
import os
import httpx
from dotenv import load_dotenv

# Database
from backend.database import engine, Base
from backend.models import User, Bucket, IndexingState

load_dotenv()

frontend_origin = os.getenv("FRONTEND_ORIGIN")


@asynccontextmanager
async def lifespan(app: FastAPI):

    # Create DB tables (idempotent)
    print("Initializing Database...")
    Base.metadata.create_all(bind=engine)
    print("Database Ready")
    print("-"*20)

    print(
        f"Pipeline Service URL: "
        f"{app_state.pipeline_url}"
    )

    # Verify pipeline service is reachable
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{app_state.pipeline_url}/health",
                timeout=5.0
            )
            if resp.status_code == 200:
                print("Pipeline Service: Connected ✓")
            else:
                print(
                    "Pipeline Service: Responded with "
                    f"status {resp.status_code}"
                )
    except Exception as e:
        print(
            f"Pipeline Service: Not reachable "
            f"({e}). Will retry on requests."
        )

    print("-"*20)
    print("CRM API Service Ready!")

    yield

    print("Shutting down...")


app = FastAPI(
    title="AI Face Recognition API", lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        frontend_origin,
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# @app.post("/login")
# async def login():
#     return {"message": "success"}




@app.get("/")
def home():
    return {
        "message": "AI Face Recognition API Running"
    }


@app.get("/health")
async def health():
    """
    Health check — also checks pipeline service health.
    """
    pipeline_healthy = False
    pipeline_data = {}

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{app_state.pipeline_url}/health",
                timeout=5.0
            )
            if resp.status_code == 200:
                pipeline_healthy = True
                pipeline_data = resp.json()
    except Exception:
        pass

    return {
        "status": "healthy",
        "pipeline_service": pipeline_healthy,
        "pipeline_details": pipeline_data
    }


@app.get("/index-stats")
async def index_stats():
    """
    Proxy to pipeline service for FAISS index stats.
    """
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{app_state.pipeline_url}/index-stats",
                timeout=10.0
            )
            return resp.json()
    except Exception as e:
        return {
            "success": False,
            "message": f"Pipeline service error: {e}"
        }


# Register routes
app.include_router(search_router)
app.include_router(auth_router)
app.include_router(indexing_router)
app.include_router(bucket_router)