import os
import pickle
import numpy as np
import faiss

from tqdm import tqdm

from backend.services.storage_service import B2Storage
from backend.services.face_engine import FaceEngine


MAX_IMAGES = 50


# -----------------------------
# CONFIG
# -----------------------------

TEMP_FOLDER = "temp"

FAISS_INDEX_PATH = "faiss_index/face_engine.bin"
MAPPING_PATH = "faiss_index/image_mapping.pkl"

os.makedirs(TEMP_FOLDER, exist_ok=True)


# -----------------------------
# INITIALIZE SERVICES
# -----------------------------

storage = B2Storage()

engine = FaceEngine()


# -----------------------------
# LOAD B2 FILES
# -----------------------------

files = storage.list_files()
files = files[:MAX_IMAGES]

print(f"\nTotal B2 Files Found: {len(files)}")


# -----------------------------
# STORE EMBEDDINGS
# -----------------------------

embeddings = []

image_mapping = {}

current_id = 0


# -----------------------------
# PROCESS FILES
# -----------------------------

for file_data in tqdm(files):

    try:

        file_name = file_data["file_name"]
        # file_url = file_data["file_url"]

        # Temp local path
        temp_path = os.path.join(
            TEMP_FOLDER,
            file_name.replace("/", "_")
        )

        # Download image
        storage.download_file(
            file_name,
            temp_path
        )

        # Generate embedding
        embedding = engine.get_embedding(temp_path)

        # Skip if no face
        if embedding is None:
            print(f"No face found: {file_name}")
            continue

        embeddings.append(embedding)

        image_mapping[current_id] = {
            "file_name": file_name,
            # "file_url": file_url
        }

        current_id += 1

        # Remove temp file
        os.remove(temp_path)

    except Exception as e:

        print(f"Error processing: {file_name}")
        print(e)


# -----------------------------
# CONVERT TO NUMPY
# -----------------------------

embeddings = np.array(
    embeddings
).astype("float32")


print("\nTotal embeddings:", len(embeddings))


# -----------------------------
# CREATE FAISS INDEX
# -----------------------------

embedding_dimension = embeddings.shape[1]

index = faiss.IndexFlatIP(
    embedding_dimension
)

index.add(embeddings)

print("FAISS index created")


# -----------------------------
# SAVE INDEX
# -----------------------------

faiss.write_index(
    index,
    FAISS_INDEX_PATH
)

print(f"Index saved: {FAISS_INDEX_PATH}")


# -----------------------------
# SAVE MAPPINGS
# -----------------------------

with open(MAPPING_PATH, "wb") as f:

    pickle.dump(image_mapping, f)

print(f"Mappings saved: {MAPPING_PATH}")


print("\nDONE")