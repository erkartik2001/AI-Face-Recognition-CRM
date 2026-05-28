import os
from dotenv import load_dotenv

load_dotenv()

# Pipeline service URL
pipeline_url = os.getenv(
    "PIPELINE_SERVICE_URL", "http://localhost:8001"
)

# Legacy references (kept for backward compatibility)
matcher = None
b2_storage = None
face_engine = None

# Sync state tracking (in-memory)
sync_in_progress = False
sync_job = None