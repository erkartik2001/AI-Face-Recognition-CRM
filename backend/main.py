from fastapi import FastAPI

from backend.routes.search_routes import router as search_router
from backend.routes.upload_routes import router as upload_router

app = FastAPI(
    title= "AI Face Recognition API"
)

@app.get("/")
def home():

    return {
        "message" :  "AI Face Recognition API Running"
    }

# Register routes
app.include_router(search_router)
app.include_router(upload_router)