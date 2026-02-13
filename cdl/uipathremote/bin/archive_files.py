import os
import shutil
from bin.global_vars import GlobalVars


def archive_files(file_name, version):
    # Moves old files to a version-based subdirectory
    # The version parameter comes from user input (e.g., "24.10.1")

    # Create version-based directory name
    version_dir = os.path.join(GlobalVars.uipath_fileshare_path, version)

    # Ensure version directory exists
    if not os.path.exists(version_dir):
        os.makedirs(version_dir)

    # Get all MSI files in the main directory
    files_to_move = [f for f in os.listdir(GlobalVars.uipath_fileshare_path)
                     if os.path.isfile(os.path.join(GlobalVars.uipath_fileshare_path, f))
                     and f.lower().endswith('.msi')]

    # Move old MSI files to the version directory
    for file in files_to_move:
        source_path = os.path.join(GlobalVars.uipath_fileshare_path, file)
        # Always name it UiPathRemoteRuntime.msi in the version folder
        destination_path = os.path.join(version_dir, "UiPathRemoteRuntime.msi")
        shutil.move(source_path, destination_path)

