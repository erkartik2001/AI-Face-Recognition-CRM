from backend.services.face_engine import FaceEngine


engine = FaceEngine()

image_path = "dataset/images.jpeg"

embedding = engine.get_embedding(image_path)

if embedding is None:
    print("No face detected")

else:
    print("Embedding Generated")
    print("Embedding Shape:", embedding.shape)
    print(embedding[:10])