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

# Guarantee only the headless OpenCV variant is present at runtime.
# 1. Pre-install headless with --no-deps so it satisfies the opencv requirement
#    during the main install without pulling in GUI dependencies.
# 2. Install all requirements normally (insightface et al. may pull in the GUI
#    variant as a transitive dependency, overwriting the headless build).
# 3. Explicitly uninstall the GUI variant and force-reinstall headless so it is
#    always the final installed package, regardless of resolution order.
RUN pip install --no-cache-dir --no-deps opencv-python-headless==4.9.0.80 && \
    pip install --no-cache-dir -r requirements.txt && \
    pip uninstall -y opencv-python && \
    pip install --no-cache-dir --force-reinstall --no-deps opencv-python-headless==4.9.0.80

# Copy application source
COPY . .

# CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
CMD ["sh", "-c", "uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
