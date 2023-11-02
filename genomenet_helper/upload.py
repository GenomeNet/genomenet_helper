import os
import subprocess
from b2sdk.v2 import InMemoryAccountInfo, B2Api
import getpass

def compress_folders(train_folder, test_folder, validation_folder, base_name):
    archive_name = f"{base_name}.tar.gz"
    subprocess.run(['tar', '-czf', archive_name, train_folder, test_folder, validation_folder], check=True)
    return archive_name

def get_folder_size_mb(folder_path):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(folder_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
    return total_size / (1024 * 1024)

def upload_dataset(train_folder, test_folder, validation_folder):
    # Assuming the folders are named with a consistent pattern: 'prefix_date'
    base_name = '_'.join(train_folder.split('_')[:-1])
    date_suffix = train_folder.split('_')[-1]

    # Compress the folders into a single archive
    archive_name = compress_folders(train_folder, test_folder, validation_folder, base_name)
    
    # Check size limit
    archive_size_gb = get_folder_size_mb(archive_name) / 1024
    if archive_size_gb > 100:
        print("The archive exceeds the 100GB size limit and will not be uploaded.")
        return

    # Get credentials from the user
    application_key_id = getpass.getpass('Enter your Backblaze B2 Application Key ID: ')
    application_key = getpass.getpass('Enter your Backblaze B2 Application Key: ')
    bucket_name = input('Enter your Backblaze B2 Bucket name: ')

    info = InMemoryAccountInfo()
    b2_api = B2Api(info)
    b2_api.authorize_account("production", application_key_id, application_key)
    bucket = b2_api.get_bucket_by_name(bucket_name)

    # Upload the file
    b2_file = bucket.upload_local_file(
        local_file=archive_name,
        file_name=os.path.basename(archive_name)
    )

    print(f"Successfully uploaded {archive_name}")
    print(f"File available at: {b2_file.file_name}")

# This function would be connected to your CLI interface
# for example as 'genomenet_helper upload --train <train_folder> --test <test_folder> --validation <validation_folder>'
