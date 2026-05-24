FROM python:3.13-slim

WORKDIR /app

# Install system dependencies required by OpenCV before any Python packages
RUN apt-get update && apt-get install -y \
    libxcb1 \
    libxrender1 \
    libxext6 \
    libsm6 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt .

# Force headless OpenCV so the GUI variant from insightface's transitive deps
# never gets installed, then install the rest of requirements normally
RUN pip install --no-cache-dir opencv-python-headless && \
    pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY . .

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
