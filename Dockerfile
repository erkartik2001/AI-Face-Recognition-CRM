FROM python:3.10-slim

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

# Install opencv-python-headless with --no-deps so pip cannot replace it with
# the GUI variant (opencv-python) when insightface's transitive deps are later
# resolved. The package is already present and satisfies the opencv requirement,
# so the subsequent full requirements install leaves it untouched.
RUN pip install --no-cache-dir --no-deps opencv-python-headless==4.9.0.80 && \
    pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY . .

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
