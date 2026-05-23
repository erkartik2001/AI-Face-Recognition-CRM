FROM python:3.10-slim

# System dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libglib2.0-0 \
    libgl1 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libxcb1 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install python packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Expose port
EXPOSE 8000

# Start app
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]