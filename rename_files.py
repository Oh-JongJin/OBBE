import os

def rename_merge_files(root_path):
    # Walk through all directories
    for dirpath, dirnames, filenames in os.walk(root_path):
        # Filter for files ending with _merge.txt
        merge_files = [f for f in filenames if f.endswith('_merge.txt')]
        
        for file in merge_files:
            # Create old and new file paths
            old_file_path = os.path.join(dirpath, file)
            new_file_name = f"{file}".replace('_merge.txt', '.txt')
            fname = new_file_name.split('_')
            new_file_name = f"{fname[0]}_{fname[2]}"
            # continue
            new_file_path = os.path.join(dirpath, new_file_name)
            
            # Rename the file
            try:
                # os.rename(old_file_path, new_file_path)
                print(f"Renamed: {file} -> {new_file_name}")
            except Exception as e:
                print(f"Error renaming {file}: {str(e)}")

# root_path = "./"
# rename_merge_files(root_path)



import os
import shutil

def move_prefixed_files(root_path, destination_path):
    # Create destination directory if it doesn't exist
    os.makedirs(destination_path, exist_ok=True)
    
    # Walk through all directories
    for dirpath, dirnames, filenames in os.walk(root_path):
        parent_folder = os.path.basename(dirpath)
        
        # Filter for files that start with the parent folder name
        for file in filenames:
            if file.startswith(parent_folder):
                # Create full paths
                source_file = os.path.join(dirpath, file)
                destination_file = os.path.join(destination_path, file)
                
                try:
                    # Move the file
                    shutil.copy(source_file, destination_file)
                    print(f"Moved: {file} -> {destination_path}")
                except Exception as e:
                    print(f"Error moving {file}: {str(e)}")

root_path = "./"
destination_path = "labels"

move_prefixed_files(root_path, destination_path)