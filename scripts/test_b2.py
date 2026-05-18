from backend.services.storage_service import B2Storage

storage = B2Storage()

files = storage.list_files()

print("\nBUCKET FILES:\n")

for file in files:
    print(file)