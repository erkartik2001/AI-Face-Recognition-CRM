from backend.services.storage_service import B2Storage


storage = B2Storage()


file_name = "shyam-pasfoto-346daad5a5bb54a81d5b62fc043476af.jpg"


save_path = "query.jpg"


storage.download_file(
    file_name,
    save_path
)


print("Downloaded:", save_path)