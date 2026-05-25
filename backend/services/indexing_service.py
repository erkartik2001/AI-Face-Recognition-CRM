import os
import json
import pickle
import numpy as np
import faiss
from datetime import datetime

import backend.app_state as app_state


INDEXING_STATE_PATH = "faiss_index/indexing_state.json"
FAISS_INDEX_PATH = "faiss_index/face_engine.index"
MAPPING_PATH = "faiss_index/image_mapping.pkl"
TEMP_FOLDER = "temp"


class IndexingService:

    def __init__(self):

        os.makedirs(TEMP_FOLDER, exist_ok=True)

        self.storage = app_state.b2_storage
        self.engine = app_state.face_engine

    # =========================================
    # STATE MANAGEMENT (per-bucket)
    # =========================================

    def load_state(self):
        """
        Load per-bucket indexing state.
        Migrates old format {"last_indexed": N}
        to new format {"bucket_name": {...}} on first call.
        """

        if not os.path.exists(INDEXING_STATE_PATH):
            return {}

        with open(INDEXING_STATE_PATH, "r") as f:
            state = json.load(f)

        # Migrate old single-bucket format
        if "last_indexed" in state and isinstance(
            state.get("last_indexed"), int
        ):
            old_last = state["last_indexed"]
            bucket_name = os.getenv(
                "B2_BUCKET_NAME", "unknown"
            )

            new_state = {
                bucket_name: {
                    "last_indexed": old_last,
                    "total_files": None,
                    "last_sync_date": None
                }
            }

            self.save_state(new_state)
            return new_state

        return state

    def save_state(self, state):

        os.makedirs(
            os.path.dirname(INDEXING_STATE_PATH),
            exist_ok=True
        )

        with open(INDEXING_STATE_PATH, "w") as f:
            json.dump(state, f, indent=4)

    # =========================================
    # FAISS INDEX MANAGEMENT
    # =========================================

    def load_index_and_mapping(self):

        index = None
        image_mapping = {}

        if os.path.exists(FAISS_INDEX_PATH):
            index = faiss.read_index(FAISS_INDEX_PATH)

        if os.path.exists(MAPPING_PATH):
            with open(MAPPING_PATH, "rb") as f:
                image_mapping = pickle.load(f)

        return index, image_mapping

    def save_index_and_mapping(self, index, image_mapping):

        os.makedirs("faiss_index", exist_ok=True)

        if index is not None:
            faiss.write_index(
                index, FAISS_INDEX_PATH
            )

        with open(MAPPING_PATH, "wb") as f:
            pickle.dump(image_mapping, f)

    # =========================================
    # BACKGROUND INDEXING
    # =========================================

    def run_indexing(self, batch_size=50, bucket_name=None):
        """
        Run indexing for a specific bucket.
        Called from a background thread.
        Updates app_state.sync_job with live progress.
        """

        if not bucket_name:
            bucket_name = os.getenv(
                "B2_BUCKET_NAME", "icf-bucket"
            )

        try:
            app_state.sync_job["status"] = "running"
            app_state.sync_job["bucket"] = bucket_name

            # ---------------------------------
            # Load per-bucket state
            # ---------------------------------

            state = self.load_state()

            bucket_state = state.get(bucket_name, {
                "last_indexed": 0,
                "total_files": None,
                "last_sync_date": None
            })

            last_indexed = bucket_state.get(
                "last_indexed", 0
            )

            # ---------------------------------
            # List files from bucket
            # ---------------------------------

            print(f"Listing files from bucket: {bucket_name}")

            all_files = self.storage.list_files_in_bucket(
                bucket_name
            )

            total_files = len(all_files)

            print(f"Total files in bucket: {total_files}")

            app_state.sync_job["total_files"] = total_files
            app_state.sync_job["remaining"] = max(
                0, total_files - last_indexed
            )

            # ---------------------------------
            # Get batch to process
            # ---------------------------------

            files = all_files[
                last_indexed:last_indexed + batch_size
            ]

            if not files:

                app_state.sync_job["status"] = "completed"
                app_state.sync_job["message"] = (
                    "No new files to index"
                )

                bucket_state["total_files"] = total_files
                state[bucket_name] = bucket_state
                self.save_state(state)

                app_state.sync_in_progress = False
                return

            # ---------------------------------
            # Load existing FAISS + mapping
            # ---------------------------------

            index, image_mapping = (
                self.load_index_and_mapping()
            )

            current_id = len(image_mapping)

            new_embeddings = []
            processed = 0
            skipped = 0

            # ---------------------------------
            # Process each file
            # ---------------------------------

            for file_data in files:

                file_name = file_data["file_name"]

                temp_path = os.path.join(
                    TEMP_FOLDER,
                    file_name.replace("/", "_")
                )

                try:

                    # Download from bucket
                    self.storage.download_file_from_bucket(
                        file_name, temp_path, bucket_name
                    )

                    # Generate embedding
                    embedding = self.engine.get_embedding(
                        temp_path
                    )

                    if embedding is None:
                        skipped += 1
                        continue

                    new_embeddings.append(embedding)

                    image_mapping[current_id] = {
                        "file_name": file_name,
                        "bucket_name": bucket_name
                    }

                    current_id += 1
                    processed += 1

                    # Update live progress
                    app_state.sync_job["processed"] = processed
                    app_state.sync_job["skipped"] = skipped

                except Exception as e:
                    print(
                        f"Error processing {file_name}: {e}"
                    )
                    skipped += 1

                finally:
                    if os.path.exists(temp_path):
                        try:
                            os.remove(temp_path)
                        except OSError:
                            pass

            # ---------------------------------
            # Add embeddings to FAISS
            # ---------------------------------

            if new_embeddings:

                embeddings_np = np.array(
                    new_embeddings
                ).astype("float32")

                if index is None:
                    dimension = embeddings_np.shape[1]
                    index = faiss.IndexFlatIP(dimension)

                index.add(embeddings_np)

                self.save_index_and_mapping(
                    index, image_mapping
                )

            # ---------------------------------
            # Update per-bucket state
            # ---------------------------------

            new_last = last_indexed + len(files)

            bucket_state["last_indexed"] = new_last
            bucket_state["total_files"] = total_files
            bucket_state["last_sync_date"] = (
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )

            state[bucket_name] = bucket_state
            self.save_state(state)

            # ---------------------------------
            # Reload matcher with new index
            # ---------------------------------

            try:
                from backend.matcher import FaceMatcher
                app_state.matcher = FaceMatcher()
                print("Matcher reloaded after indexing")
            except Exception as e:
                print(
                    f"Warning: Failed to reload matcher: {e}"
                )

            # ---------------------------------
            # Mark completed
            # ---------------------------------

            app_state.sync_job["status"] = "completed"
            app_state.sync_job["processed"] = processed
            app_state.sync_job["skipped"] = skipped
            app_state.sync_job["total_files"] = total_files
            app_state.sync_job["remaining"] = max(
                0, total_files - new_last
            )
            app_state.sync_job["completed_at"] = (
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )

            print(
                f"Indexing completed: {processed} processed, "
                f"{skipped} skipped from '{bucket_name}'"
            )

        except Exception as e:
            print(f"Indexing failed: {e}")
            app_state.sync_job["status"] = "failed"
            app_state.sync_job["error"] = str(e)

        finally:
            app_state.sync_in_progress = False

    # =========================================
    # SYNC LOGS
    # =========================================

    def get_sync_logs(self):
        """Get per-bucket sync statistics."""

        state = self.load_state()
        logs = []

        for bucket_name, bucket_state in state.items():

            total_files = bucket_state.get("total_files")
            last_indexed = bucket_state.get(
                "last_indexed", 0
            )

            logs.append({
                "bucket_name": bucket_name,
                "total_synced": last_indexed,
                "total_files": total_files,
                "remaining": (
                    max(0, total_files - last_indexed)
                    if total_files is not None
                    else None
                ),
                "last_sync_date": bucket_state.get(
                    "last_sync_date"
                )
            })

        return logs