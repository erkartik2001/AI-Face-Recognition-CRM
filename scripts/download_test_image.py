from backend.services.storage_service import B2Storage


storage = B2Storage()


file_name = "0ED566F5-A9DA-4BCF-817F-1B8251F8456D-0f483d838d9589f64382b9e278ebc052.jpeg"


save_path = "query.jpg"


storage.download_file(
    file_name,
    save_path
)


print("Downloaded:", save_path)