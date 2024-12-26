"""Rename the files in 'data' to short the names"""

import os
import shutil

directory = "data"
new_directory = os.path.join(directory, "renamed")

files = os.listdir(directory)


from phdtools.filetools import rename_and_copy


for i, each_file in enumerate(files):
    if "M2" not in each_file and "M1" not in each_file:
        continue
        # raise Exception(f"Error in file '{each_file}'")


    rename_and_copy(each_file, directory, new_directory=new_directory)

print("Done")