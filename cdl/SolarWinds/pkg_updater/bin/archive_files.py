import os
import shutil
import datetime
from bin.global_vars import GlobalVars


def archive_files(file_name):
    # puts the old files in a dated subdirectory (it will move only the specified file, such that was selected for
    #  upload)

    today = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    bkp_dir = os.path.join(GlobalVars.solarwinds_fileshare_path, today)

    # ensure Archive directory exists
    if not os.path.exists(bkp_dir):
        os.makedirs(bkp_dir)

    files_to_move = [f for f in os.listdir(GlobalVars.solarwinds_fileshare_path) if os.path.isfile(os.path.join(GlobalVars.solarwinds_fileshare_path, f))]

    for file in files_to_move:
        if file_name == file:
            source_path = os.path.join(GlobalVars.solarwinds_fileshare_path, file)
            destination_path = os.path.join(bkp_dir, file)
            shutil.move(source_path, destination_path)
