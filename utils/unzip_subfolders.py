import os
import zipfile

def unzip_subfolders(main_folder):
    metabolights_folder = os.path.join(main_folder, 'Metabolights')
    
    if not os.path.exists(metabolights_folder):
        print(f"Error: {metabolights_folder} does not exist.")
        return

    for subfolder in os.listdir(metabolights_folder):
        subfolder_path = os.path.join(metabolights_folder, subfolder)
        
        if os.path.isdir(subfolder_path):
            zip_files = [f for f in os.listdir(subfolder_path) if f.endswith('.zip')]
            
            if zip_files:
                zip_file = zip_files[0]  # Assume there's only one zip file
                zip_path = os.path.join(subfolder_path, zip_file)
                
                try:
                    # Create a new folder with the same name as the zip file (minus .zip extension)
                    extract_folder_name = os.path.splitext(zip_file)[0]
                    extract_folder_path = os.path.join(subfolder_path, extract_folder_name)
                    os.makedirs(extract_folder_path, exist_ok=True)

                    # Extract contents to the new folder
                    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                        zip_ref.extractall(extract_folder_path)
                    print(f"Unzipped: {zip_path} to {extract_folder_path}")
                    
                    # Delete the zip file after successful extraction
                    os.remove(zip_path)
                    print(f"Deleted: {zip_path}")

                    # Rename files within the extracted folder
                    for root, _, files in os.walk(extract_folder_path):
                        for file_name in files:
                            if '_compressed_files' in file_name:
                                new_name = file_name.replace('_compressed_files', '')
                                old_file_path = os.path.join(root, file_name)
                                new_file_path = os.path.join(root, new_name)
                                os.rename(old_file_path, new_file_path)
                                print(f"Renamed: {old_file_path} to {new_file_path}")

                    # Rename the extracted folder if it contains '_compressed_files'
                    if '_compressed_files' in extract_folder_name:
                        new_extract_folder_name = extract_folder_name.replace('_compressed_files', '')
                        new_extract_folder_path = os.path.join(subfolder_path, new_extract_folder_name)
                        os.rename(extract_folder_path, new_extract_folder_path)
                        print(f"Renamed folder: {extract_folder_path} to {new_extract_folder_path}")
                    
                except zipfile.BadZipFile:
                    print(f"Error: {zip_path} is not a valid zip file. Skipping.")
                except Exception as e:
                    print(f"Error processing {zip_path}: {str(e)}")

main_folder = ''  # Add the path to the main folder containing the Metabolights subfolders - make sure the main folder is unzipped
unzip_subfolders(main_folder)
