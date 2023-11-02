import os
import shutil

def merge_directories(source_dirs, destination_dir):
    # Create destination directory if it doesn't exist
    if not os.path.exists(destination_dir):
        os.makedirs(destination_dir)

    # Copy all files from source directories to destination directory
    for dir_path in source_dirs:
        for filename in os.listdir(dir_path):
            src_file = os.path.join(dir_path, filename)
            dst_file = os.path.join(destination_dir, filename)
            if os.path.isfile(src_file):
                # In case of file name conflicts, you can customize how to handle them here
                shutil.copy2(src_file, dst_file)
            elif os.path.isdir(src_file):
                # Handle sub-directories if necessary
                merge_directories([src_file], os.path.join(destination_dir, filename))

def merge_datasets(input_base, date):
    # Define the expected directories
    subsampled_prefix = f"{input_base}_train_subsampled_{date}"
    simulated_prefix = f"{input_base}_train_simulated_{date}"

    categories = ['train', 'test', 'validation']
    processes = ['subsampled', 'simulated']

    for category in categories:
        source_dirs = [
            f"{input_base}_{category}_{process}_{date}"
            for process in processes
        ]

        destination_dir = f"{input_base}-merged/{category}"

        # Check if all the source directories exist
        if all(os.path.exists(src) for src in source_dirs):
            merge_directories(source_dirs, destination_dir)
        else:
            missing_dirs = [src for src in source_dirs if not os.path.exists(src)]
            print(f"Error: The following directories are missing and required for merging: {', '.join(missing_dirs)}")
            return  # Exit the function if any directories are missing

    print(f"Datasets merged successfully into {input_base}-merged directory.")
