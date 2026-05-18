import pickle
import numpy as np
import faiss

from backend.services.face_engine import FaceEngine


class FaceMatcher:

    def __init__(
        self,
        faiss_index_path="faiss_index/face_engine.bin",
        mapping_path="faiss_index/image_mapping.pkl"
    ):

        print("Loading Face Matcher...")

        # Load face engine
        self.engine = FaceEngine()

        # Load FAISS index
        self.index = faiss.read_index(faiss_index_path)

        # Load image mappings
        with open(mapping_path, "rb") as f:
            self.image_mapping = pickle.load(f)

        print("Face Matcher Ready")


    def search(
        self,
        image_path,
        top_k=5,
        threshold=0.5
    ):

        # Generate embedding
        embedding = self.engine.get_embedding(image_path)

        if embedding is None:
            return []

        query_embedding = np.array([embedding]).astype("float32")

        # Search FAISS
        similarities, indices = self.index.search(
            query_embedding,
            top_k
        )

        results = []

        for similarity, idx in zip(
            similarities[0],
            indices[0]
        ):

            if similarity < threshold:
                continue

            matched_data = self.image_mapping[idx]

            results.append({
                "person": matched_data["person"],
                "image_path": matched_data["image_path"],
                "similarity": float(similarity)
            })

        return results