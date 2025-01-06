import shutil
import os

def rename(file):
    """Rename files to remove extra info in name after XX or XY.

    If the file has 'intervalmarker' in its name, we keep that in the name.

    Parameters
    ----------
    file : str
        File name

    Returns
    -------
    str
        New file name
    """
    to_delete =  "_".join(file.split("_")[5:])
    extension = file.split(".")[-1]
    new_file_name = file.replace(to_delete, "")[:-1].upper()

    if "intervalmarker".upper() in file.upper():
        print(f"Interval in {file}")
        new_file_name = new_file_name + "_intervalmarket"

    if file.endswith(".md.edf"):
        extension = "md" + "." + extension

    return new_file_name + "." + extension


def copy(old_file_path, new_file_path):
    """Copy file from old path to new path

    Parameters
    ----------
    old_file_path : str
        Old path string
    new_file_path : str
        New path string
    """
    shutil.copyfile(old_file_path, new_file_path)


def rename_and_copy(each_file, old_directory, new_directory=None):
    """Rename and copy file according to rename.

    Parameters
    ----------
    each_file : str
        File name
    directory : str
        New directory

    Examples
    --------
    You can rename the files from a directory using:

    >>> import os
    >>> import shutil
    >>> directory = "data"
    >>> new_directory = os.path.join(directory, "renamed")
    >>> files = os.listdir(directory)
    >>> from phdtools.filetools import rename_and_copy
    >>> for i, each_file in enumerate(files):
    >>>     rename_and_copy(each_file, directory, new_directory=new_directory)
    """

    if os.path.isdir(os.path.join(old_directory, each_file)):
        print(f"{each_file} is a directory")
        return

    if new_directory is None:
        # Default new diretory is the old directory
        new_directory = old_directory

    new_file_name = rename(each_file)

    old_file_path = os.path.join(old_directory, each_file)
    new_file_path = os.path.join(new_directory, new_file_name)

    print(f"Copied '{old_file_path}' to '{new_file_path}'.")
    copy(old_file_path, new_file_path)

