import pickle
import numpy as np
import faiss
import os

from backend.services.face_engine import FaceEngine
from backend.services.storage_service import B2Storage


class FaceMatcher:

    def __init__(
        self,
        faiss_index_path="faiss_index/face_engine.bin",
        mapping_path="faiss_index/image_mapping.pkl"
    ):

        print("Loading Face Matcher...")

        # Load face engine
        self.engine = FaceEngine()

        # b2
        self.storage = B2Storage()


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

            # results.append({
            #     "person": matched_data["person"],
            #     "image_path": matched_data["image_path"],
            #     "similarity": float(similarity)
            # })

            file_name = matched_data["file_name"]

            file_url = self.storage.generate_file_url(file_name)

            results.append({
                "file_name":file_name,
                "file_url" : file_url,
                "similarity":float(similarity)
            })

        return results
    

    def add_face(
        self,
        embedding,
        file_name,
        file_url
    ):

        # Convert embedding
        embedding = np.array(
            [embedding]
        ).astype("float32")


        # Add to FAISS
        self.index.add(embedding)


        # New vector ID
        new_id = len(self.image_mapping)


        # Update mapping
        self.image_mapping[new_id] = {
            "file_name": file_name,
            "file_url": file_url
        }


        # Save updated FAISS index
        faiss.write_index(
            self.index,
            "faiss_index/face_engine.bin"
        )


        # Save updated mappings
        with open(
            "faiss_index/image_mapping.pkl",
            "wb"
        ) as f:

            pickle.dump(
                self.image_mapping,
                f
            )

        return True