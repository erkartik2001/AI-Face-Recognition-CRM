from backend.services.storage_service import B2Storage


storage = B2Storage()


file_name = "HAMIZAN-ABDULLAH-PHOTO-be4e0ed4d79a30e903b445eecfd51bf5.png"


save_path = "query2.jpg"


storage.download_file(
    file_name,
    save_path
)


print("Downloaded:", save_path)