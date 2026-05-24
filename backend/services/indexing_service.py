import os
import json
import pickle
import numpy as np
import faiss

from tqdm import tqdm


import backend.app_state as app_state


class IndexingService:

    def __init__(self):

        self.TEMP_FOLDER = "temp"

        self.FAISS_INDEX_PATH = (
            "faiss_index/face_engine.index"
        )

        self.MAPPING_PATH = (
            "faiss_index/image_mapping.pkl"
        )

        self.STATE_PATH = (
            "faiss_index/indexing_state.json"
        )

        os.makedirs(
            self.TEMP_FOLDER,
            exist_ok=True
        )


        self.storage = app_state.b2_storage
        self.engine = app_state.face_engine



    def start_indexing(
        self,
        batch_size=50
    ):

        # -----------------------------
        # LOAD STATE
        # -----------------------------

        with open(self.STATE_PATH, "r") as f:

            state = json.load(f)

        last_indexed = state["last_indexed"]

        # -----------------------------
        # LOAD FILES
        # -----------------------------

        all_files = self.storage.list_files()

        files = all_files[
            last_indexed:last_indexed + 1
        ]

        # -----------------------------
        # LOAD OR CREATE FAISS
        # -----------------------------

        if os.path.exists(
            self.FAISS_INDEX_PATH
        ):

            index = faiss.read_index(
                self.FAISS_INDEX_PATH
            )

        else:

            index = None

        # -----------------------------
        # LOAD MAPPINGS
        # -----------------------------

        if os.path.exists(
            self.MAPPING_PATH
        ):

            with open(
                self.MAPPING_PATH,
                "rb"
            ) as f:

                image_mapping = pickle.load(f)

        else:

            image_mapping = {}

        current_id = len(image_mapping)

        new_embeddings = []

        processed = 0

        # -----------------------------
        # PROCESS FILES
        # -----------------------------


        for file_data in files:

            if not batch_size:

                try:

                    file_name = file_data["file_name"]

                    temp_path = os.path.join(
                        self.TEMP_FOLDER,
                        file_name.replace("/", "_")
                    )

                    # DOWNLOAD
                    self.storage.download_file(
                        file_name,
                        temp_path
                    )


                    # EMBEDDING
                    embedding = (
                        self.engine.get_embedding(
                            temp_path
                        )
                    )

                    # REMOVE TEMP
                    os.remove(temp_path)

                    if embedding is None:

                        continue

                    new_embeddings.append(
                        embedding
                    )

                    image_mapping[current_id] = {

                        "file_name": file_name

                    }

                    current_id += 1

                    processed += 1

                    break

                except Exception as e:

                    print(e)

            # -----------------------------
            # NO EMBEDDINGS
            # -----------------------------

                if len(new_embeddings) == 0:

                    return {

                        "success": False,
                        "message": "No embeddings generated"
                    }

        # -----------------------------
        # NUMPY
        # -----------------------------

        if not batch_size:

            new_embeddings = np.array(
                new_embeddings
            ).astype("float32")

            # -----------------------------
            # CREATE FAISS
            # -----------------------------

            if index is None:

                dimension = (
                    new_embeddings.shape[1]
                )

                index = faiss.IndexFlatIP(
                    dimension
                )

            # -----------------------------
            # APPEND
            # -----------------------------

            index.add(new_embeddings)

            # -----------------------------
            # SAVE FAISS
            # -----------------------------

            faiss.write_index(
                index,
                self.FAISS_INDEX_PATH
            )

            # -----------------------------
            # SAVE MAPPINGS
            # -----------------------------

            with open(
                self.MAPPING_PATH,
                "wb"
            ) as f:

                pickle.dump(
                    image_mapping,
                    f
                )

        # -----------------------------
        # UPDATE STATE
        # -----------------------------

        state["last_indexed"] = (

            last_indexed + batch_size

        )

        with open(
            self.STATE_PATH,
            "w"
        ) as f:

            json.dump(
                state,
                f,
                indent=4
            )

        return {

            "success": True,

            "processed": processed,

            "last_indexed":
                state["last_indexed"],

            "total_vectors":
                index.ntotal
        }