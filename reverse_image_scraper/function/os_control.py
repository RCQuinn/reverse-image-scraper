# Standard library imports
import os
from time import sleep

# Local imports
from ..common.colors import ColorCodes as cc


def get_main_dir():
    """ Finds parent directory.
    :return: Full file path to parent directory.
    """
    directory = os.path.dirname(__file__)
    index = directory[:directory.rfind("\\")].rfind("\\")  # find index of second last "\"
    return directory[:index]  # Return everything up to that last backslash


def exceed_NTFS_file_limit(directory):
    """ Bypasses file path character limit.
    :param directory: Directory to append prefix to.
    :return: Extended directory.
    """
    if directory[0] == "\\":  # If directory starts with \
        directory = directory[1:]
    extended_dir = "\\\\?\\" + directory  # '\\?' prefix is a special long path in Windows 10
    return extended_dir


def join_dir(*directories):
    """ Joins an list of strings with backslashes.
    :param directories: List of strings (Usually in directory format) in the order to be joined.
    :return: A single string containing fill directory.
    """
    full_dir = ""
    for name in directories:  # Loop through arbitrary length list
        full_dir = os.path.join(full_dir, name)  # Combine each element in the list with a '\'
    return full_dir


def list_dir(directory):
    """ Get a list of folders and files in directory.
    :param directory: Location to search through.
    :return: A list of names
    """
    return os.listdir(directory)


def remove_empty_dir(directory):
    """ Delete empty folder.
    :param directory: Folder to be deleted.
    """
    if len(os.listdir(directory)) == 0:  # Check if the directory is empty
        os.rmdir(directory)  # Permanently delete the directory


def make_note(directory, title):
    """ Create empty file with message as title.
    :param directory: Location to create file.
    :param title: Message.
    """
    note = open(join_dir(directory, title), 'a+')
    note.close()


def save_image(img, directory):
    """ Saves an image to specified directory.
    :param img: Image to be saved.
    :param directory: Location to save to.
    :return: Boolean whether the image saved or not.
    """
    tries = 0  # Count of attempts to save the image.
    try_limit = 10  # Max number of tries
    succeed_flag = False  # Boolean to return. Indicates if image saved successfully.
    while tries < try_limit:
        try:
            img.save(directory, img.format)  # Save image
        except OSError:  # If the image fails to save
            tries += 1
            sleep(0.1)  # Give the OS time to sort out the failed save.
        else:
            succeed_flag = True
            tries = try_limit
    img.close()
    return succeed_flag


def make_dir(name, directory):
    """ Make the new folder if it doesn't exist, else do nothing. Closes program on OS error.
    :param name: Name of folder.
    :param directory: Location to create folder in.
    :return: Full directory including folder name.
    """
    final_directory = join_dir(directory, name)  # Combine paths with '\'
    try:
        if not os.path.exists(final_directory):  # Check path does NOT exist
            os.makedirs(final_directory)  # Create folder
        return final_directory
    except OSError:  # Critical error if OS fails to create folder. Cannot progress
        print(cc.RED + cc.BOLD + "Creation of the directory %s failed." % final_directory + cc.RESET)
        exit()


def move_file(filename, source, destination):
    """ Attempts to move file. If moving would cause data loss, then the file is renamed until it can be moved safely.
    :param filename: File to move.
    :param source: Current location of the file to be moved.
    :param destination: New location of the file.
    """
    filename_new = filename  # Copy of name for editing

    index = filename.rfind(".")  # Find index of separation between name and extension
    title = filename[:index]  # Record file's name
    extension = filename[index:]  # Record file's data type extension

    can_move = False
    count = 1
    while not can_move:  # Continue until file can be moved
        try:
            os.rename(source + filename, destination + filename_new)    # Move file to new location
            can_move = True
        except FileExistsError:  # File name is already taken
            filename_new = title + "(" + str(count) + ")" + extension  # Increment file name
            count += 1
