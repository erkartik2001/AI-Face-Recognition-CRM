
"""
- Read all images from dataset
- Generate embeddings
- Store vectors
- Create faiss index
- Save index to disk
- Then database become searchable
"""

import os
import pickle
import numpy as np
from tqdm import tqdm
import faiss
from backend.services.face_engine import FaceEngine


# --------------------------
# CONFIG
# --------------------------

DATASET_PATH = "dataset"
FAISS_INDEX_PATH = "faiss_index/face_engine.bin"
MAPPING_PATH = "faiss_index/image_mapping.pkl"


# ---------------------------
# INITIALIZE FACE ENGINE
# ---------------------------

engine = FaceEngine()

# --------------------------
# STORE DATA
# --------------------------

embeddings = []
image_mapping = {}

current_id = 0


# -------------------------
# READ DATASET
# -------------------------

for person_name in os.listdir(DATASET_PATH):
    
    person_folder = os.path.join(DATASET_PATH, person_name)

    if not os.path.isdir(person_folder):
        continue

    print(f"\nProcessing: {person_name}")

    for image_name in tqdm(os.listdir(person_name)):

        image_path = os.path.join(person_folder, image_name)

        try:

            embedding = engine.get_embedding(image_path)

            # Skip if no face detected
            if embedding is None:
                print(f"No face found: {image_path}")
                continue

            embeddings.append(embedding)

            image_mapping[current_id] = {
                "person" : person_name,
                "image_path" : image_path
            }

            current_id +=1

        except Exception as e:
            print(f"Error processing {image_path}")
            print(e)


# -------------------------
# CONVERT TO NUMPY
# -------------------------

embeddings = np.array(embeddings).astype("float32")

print("\nTotal embeddings:", len(embeddings))


# -------------------------
# CREATE FAISS INDEX
# -------------------------

embedding_dimension = embeddings.shape[1] # real shape [n,512] where n = no. of images

index = faiss.IndexFlatIP(embedding_dimension) #inner product similarity, since embeddings are normalized, inner product = cosine similarity

index.add(embeddings)

print("Faiss index created")


# -------------------------
# SAVE FAISS INDEX
# -------------------------

faiss.write_index(index, FAISS_INDEX_PATH)
print(f"FAISS index saved: {FAISS_INDEX_PATH}")

# -------------------------
# SAVE IMAGE MAPPING
# -------------------------

with open(MAPPING_PATH, "wb") as f:
    pickle.dump(image_mapping, f)


print(f"Image mapping saved: {MAPPING_PATH}")

print("\nDONE")