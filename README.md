# AI Face Recognition CRM

## Project Overview

This project is a simple AI-based face recognition system.

The system compares a newly uploaded image with existing images stored in Backblaze B2 cloud storage and returns matching persons/images inside a dashboard (CRM).

The main goal of the project is to build a reliable face recognition pipeline first, then connect it with API and dashboard components.

---

# Tech Stack

| Component | Technology |
|---|---|
| Frontend Dashboard | Streamlit |
| Backend API | FastAPI |
| Face Recognition | InsightFace |
| Vector Search | FAISS |
| Storage | Backblaze B2 |
| Database | SQLite |
| Language | Python |

---

# Final Project Architecture

```text
project/
│
├── backend/
│   │
│   ├── main.py
│   ├── config.py
│   │
│   ├── routes/
│   │   ├── search_routes.py
│   │   └── upload_routes.py
│   │
│   ├── services/
│   │   ├── face_engine.py
│   │   ├── matcher.py
│   │   ├── faiss_manager.py
│   │   ├── storage_service.py
│   │   └── db_service.py
│   │
│   └── database/
│       ├── database.py
│       └── models.py
│
├── frontend/
│   │
│   ├── app.py
│   │
│   └── pages/
│       ├── upload.py
│       ├── dashboard.py
│       └── history.py
│
├── dataset/
│   ├── person_1/
│   ├── person_2/
│   └── person_3/
│
├── faiss_index/
│   ├── face_index.bin
│   └── image_mapping.pkl
│
├── scripts/
│   ├── generate_embeddings.py
│   ├── rebuild_index.py
│   └── test_pipeline.py
│
├── uploads/
│
├── requirements.txt
│
├── .env
│
└── README.md
```

---

# Architecture Explanation

The project is divided into 3 major parts:

---

# 1. Face Recognition Pipeline

This is the core AI system.

Responsible for:
- face detection
- embedding generation
- similarity search
- face matching

Main files:

```text
backend/services/
```

---

# 2. Backend API

Responsible for:
- receiving uploaded images
- returning search results
- connecting frontend with AI pipeline

Main files:

```text
backend/routes/
```

---

# 3. Frontend Dashboard

Responsible for:
- image upload UI
- displaying matched faces
- login/dashboard pages

Main files:

```text
frontend/
```

---

# System Flow

```text
User Uploads Image
        ↓
FastAPI Receives Image
        ↓
Face Detection
        ↓
Embedding Generation
        ↓
FAISS Similarity Search
        ↓
Top Matches Returned
        ↓
Results Displayed In Streamlit Dashboard
```

---

# Detailed File Explanation

---

# backend/main.py

Main FastAPI application.

Responsibilities:
- start backend server
- register API routes
- initialize application

---

# backend/config.py

Stores:
- environment variables
- B2 credentials
- database paths
- threshold settings

---

# backend/routes/

Contains API endpoints.

---

## search_routes.py

Handles:
- face search requests

Example endpoint:

```text
POST /search-face
```

---

## upload_routes.py

Handles:
- adding new images to system

Example endpoint:

```text
POST /upload-face
```

---

# backend/services/

Contains core business + AI logic.

---

## face_engine.py

Responsible for:
- loading InsightFace model
- face detection
- embedding extraction

Output:

```python
embedding.shape = (512,)
```

---

## matcher.py

Responsible for:
- similarity comparison
- confidence scoring
- threshold filtering

---

## faiss_manager.py

Responsible for:
- creating FAISS index
- loading FAISS index
- saving embeddings
- nearest-neighbor search

---

## storage_service.py

Responsible for:
- uploading images to Backblaze B2
- retrieving image URLs

---

## db_service.py

Responsible for:
- saving metadata
- saving search history
- retrieving image records

---

# backend/database/

Database-related files.

---

## database.py

Creates database connection.

---

## models.py

Defines tables/models.

Example:
- users
- images
- search_history

---

# frontend/app.py

Main Streamlit app.

Responsible for:
- dashboard routing
- authentication
- navigation

---

# frontend/pages/

Contains dashboard pages.

---

## upload.py

Image upload interface.

---

## dashboard.py

Displays:
- matched faces
- confidence scores
- uploaded images

---

## history.py

Displays:
- previous searches
- logs

---

# dataset/

Local testing dataset.

Used during development before full B2 integration.

Example:

```text
dataset/
   ├── virat/
   ├── messi/
   └── robert/
```

---

# faiss_index/

Stores vector index.

---

## face_index.bin

Stores FAISS embeddings index.

---

## image_mapping.pkl

Maps FAISS vector IDs to image paths.

---

# scripts/

Development/testing scripts.

---

## generate_embeddings.py

Reads dataset images and creates embeddings.

---

## rebuild_index.py

Recreates FAISS index if needed.

---

## test_pipeline.py

Used for local testing.

Flow:

```text
query image
     ↓
generate embedding
     ↓
search FAISS
     ↓
return top matches
```

---

# uploads/

Stores temporary uploaded images.

---

# Face Recognition Flow

---

# Step 1 — Face Detection

Detect face from uploaded image.

Uses:
- InsightFace detector

---

# Step 2 — Embedding Generation

Convert face into vector embedding.

Example:

```python
[0.21, -0.55, 0.92, ...]
```

---

# Step 3 — Similarity Search

Search nearest embeddings using FAISS.

---

# Step 4 — Match Results

Return:
- matched images
- similarity score
- confidence level

---

# Matching Logic

Cosine similarity is used.

Example:

```python
if similarity > 0.65:
    match_found = True
```

Threshold can be adjusted experimentally.

---

# Development Flow

---

# Phase 1 — Build Pipeline

Goal:

```text
query image
    ↓
find matching faces
```

No frontend focus initially.

---

# Phase 2 — Build API

Connect:
- upload endpoint
- search endpoint

---

# Phase 3 — Build Dashboard

Add:
- upload UI
- results UI
- login system

---

# Phase 4 — Integrate Backblaze B2

Replace local storage with cloud image storage.

---

# Running Backend

```bash
uvicorn backend.main:app --reload
```

---

# Running Frontend

```bash
streamlit run frontend/app.py
```

---

# Environment Variables

Example `.env`

```env
B2_KEY_ID=xxxx
B2_APPLICATION_KEY=xxxx
B2_BUCKET_NAME=xxxx

DATABASE_PATH=face_db.sqlite
```

---

# Final Workflow

```text
Upload Image
      ↓
Detect Face
      ↓
Generate Embedding
      ↓
Search Similar Faces
      ↓
Return Top Matches
      ↓
Display Results In CRM Dashboard
```