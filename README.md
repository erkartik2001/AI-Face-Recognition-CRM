# AI Face Recognition CRM

AI-powered Face Recognition CRM built using:

- FastAPI
- Streamlit
- InsightFace
- FAISS
- Backblaze B2

The system allows users to:

- Search similar faces
- Upload new face images
- Continuously index images from Backblaze B2
- Manage users with admin authentication

---

# Features

## Face Recognition

- Face Detection using InsightFace
- Face Embedding Generation
- Similarity Search using FAISS
- Top Match Retrieval

---

## Backblaze B2 Integration

The system works directly with Backblaze B2 cloud storage.

Supports:

- Listing bucket images
- Downloading images for indexing
- Uploading new images
- Generating public URLs

---

## Multi User Authentication

Supports:

- Admin Login
- User Login
- Admin Create User
- Admin Change User Password
- JWT Authentication

---

# Tech Stack

| Component | Technology |
|---|---|
| Backend API | FastAPI |
| Frontend CRM | Streamlit |
| Face Recognition | InsightFace |
| Vector Search | FAISS |
| Storage | Backblaze B2 |
| Authentication | JWT |
| User Storage | JSON |
| Language | Python |

---

# Project Structure

```text
project/
│
├── backend/
│   │
│   ├── main.py
│   │
│   ├── routes/
│   │   ├── auth_routes.py
│   │   ├── search_routes.py
│   │   ├── upload_routes.py
│   │   └── indexing_routes.py
│   │
│   ├── services/
│   │   ├── face_engine.py
│   │   ├── matcher.py
│   │   ├── storage_service.py
│   │   └── indexing_service.py
│   │
│   ├── auth/
│   │   ├── auth_service.py
│   │   ├── jwt_handler.py
│   │   └── users.json
│   │
│   └── schemas/
│
├── frontend/
│   │
│   ├── app.py
│   │
│   ├── pages/
│   │   ├── login.py
│   │   ├── dashboard.py
│   │   ├── search_face.py
│   │   ├── upload_face.py
│   │   ├── indexing.py
│   │   ├── create_user.py
│   │   └── change_password.py
│   │
│   └── utils/
│       ├── api_client.py
│       ├── auth.py
│       └── session_state.py
│
├── faiss_index/
│   ├── face_engine.bin
│   └── image_mapping.pkl
│
├── temp/
│
├── uploads/
│
├── .env
│
├── requirements.txt
│
└── README.md
```

---

# System Flow

## Face Search Flow

```text
Upload Query Image
        ↓
Generate Embedding
        ↓
Search FAISS Index
        ↓
Find Similar Faces
        ↓
Return Top Match
```

---

## Upload Face Flow

```text
Upload Image
        ↓
Upload To B2
        ↓
Generate Embedding
        ↓
Append To FAISS
        ↓
Update Mapping
```

---

## Indexing Flow

```text
Read Images From B2
        ↓
Download Temp Image
        ↓
Generate Embedding
        ↓
Store In FAISS
        ↓
Save Mapping
```

---

# Environment Variables

Create a `.env` file:

```env
B2_KEY_ID=YOUR_KEY_ID
B2_APPLICATION_KEY=YOUR_APPLICATION_KEY
B2_BUCKET_NAME=YOUR_BUCKET_NAME

SECRET_KEY=your_jwt_secret
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
```

---

# Install Requirements

```bash
pip install -r requirements.txt
```

---

# Run Backend

```bash
uvicorn backend.main:app --reload
```

Backend runs on:

```text
http://127.0.0.1:8000
```

Swagger Docs:

```text
http://127.0.0.1:8000/docs
```

---

# Run Frontend

```bash
streamlit run frontend/app.py
```

Frontend runs on:

```text
http://localhost:8501
```

---

# Admin Capabilities

Admin can:

- Login
- Create Users
- Change User Passwords
- Start B2 Indexing
- Upload Faces
- Search Faces

---

# User Capabilities

Users can:

- Login
- Search Faces
- Upload Faces

Users CANNOT:

- Create Users
- Change Other User Passwords
- Start Indexing

---

# FAISS Files

## face_engine.bin

Stores:

- Face Embeddings
- Vector Search Index

---

## image_mapping.pkl

Maps:

```python
vector_id -> file_name
```

Used to retrieve matched images from B2.

---

# Important Notes

## Indexing Is Required First

Before searching faces:

- images must be indexed first

Use:

```text
Index Images Page
```

or

```text
/start-indexing
```

API.

---

## Corrupted Images

Some B2 images may be corrupted or truncated.

System automatically:

- skips invalid images
- continues indexing

---

# Authentication System

Authentication uses:

- JWT Tokens
- Password Hashing
- JSON User Storage

No database required for MVP.

---

# Future Improvements

Possible future upgrades:

- PostgreSQL Database
- Background Indexing Queue
- GPU Inference
- Face Clustering
- Video Face Recognition
- Search History
- Role Permissions
- Docker Deployment
- Async Processing
- Real-Time Index Monitoring

---

# MVP Goal

This project is designed as a lightweight MVP CRM for:

- Face Matching
- Face Search
- Cloud Image Retrieval
- Multi User Access

Optimized for fast deployment and low infrastructure complexity.
