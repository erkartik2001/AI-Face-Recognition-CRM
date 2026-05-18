#downloads one of the indexed image for testing.
import pickle


MAPPING_PATH = "faiss_index/image_mapping.pkl"


with open(MAPPING_PATH, "rb") as f:
    mappings = pickle.load(f)


print("\nINDEXED IMAGES:\n")


for idx, data in mappings.items():

    print(f"ID: {idx}")
    print(f"File Name: {data['file_name']}")
    print("-" * 50)