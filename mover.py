import os
import shutil


"""
@params: top_folder_name
how?
for all files in each top_folder_name:
move the files to top_folder_name
"""


def file_mover(top_folder_name):
    """
    move the file
    """
    base_dir = os.path.join(os.getcwd(), "assets", top_folder_name)
    dir = []

    for i in os.listdir(base_dir):  # h
        if os.path.isdir(os.path.join(base_dir, i)):
            for j in os.listdir(os.path.join(base_dir, i)):
                target_file_path = os.path.join(base_dir, i, j)
                destination_file_path = os.path.join(base_dir, j)
                # move it
                shutil.move(target_file_path, destination_file_path)
                # remove 2 chars folder
        try:
            shutil.rmtree(os.path.join(base_dir, i))
        except:
            pass


# move it!!!
top_dir = os.path.join(os.getcwd(), "assets")
for d in os.listdir(top_dir):
    file_mover(d)
