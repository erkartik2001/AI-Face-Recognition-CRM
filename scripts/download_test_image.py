from backend.services.storage_service import B2Storage


storage = B2Storage()


file_name = "0-1-16283216dbacf18ff942c9440b3161d2.jpeg"


save_path = "query.jpg"


storage.download_file(
    file_name,
    save_path
)


print("Downloaded:", save_path)