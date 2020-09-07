"""Reverse Image Scraper - By RCQuinn

This script takes user images in the `./input` folder and
attempts to return larger versions of the same image from Google's
reverse image searching service.

This tool accepts images of types: (.jpg), (.jpeg), and (.png)

This script requires that `requests-html`, `pillow`, and `bs4`
be installed within the python environment you are running the
script from.
"""
# Standard library imports
import sys
import psutil
import multiprocessing
from time import time as time_now
from os.path import isdir
from functools import partial

# Third party imports
import pytest
from bs4 import SoupStrainer
from requests_html import HTMLSession

# Local imports
from .function import os_control
from .function import user_input
from .function import web_control
from .common.colors import ColorCodes as cc

# Get number of physical cores
PROCESS = psutil.cpu_count(logical=False)


def run():
    """ Main function. Calls all other functions.
    """
    OUTPUT_FOLDER = "output"
    INPUT_FOLDER = "input"
    DEFAULT_FOLDER = "(-) Default Results"

    # File setup
    current_directory = os_control.get_main_dir()  # Get folder the program is in
    current_directory = os_control.exceed_NTFS_file_limit(current_directory)  # Bypass Win 10 folder length
    input_dir = os_control.make_dir(INPUT_FOLDER, current_directory)  # Create input folder
    output_dir = os_control.make_dir(OUTPUT_FOLDER, current_directory)  # Create output folder
    default_dir = os_control.make_dir(os_control.join_dir(OUTPUT_FOLDER,  # Create default results folder
                                                          DEFAULT_FOLDER), current_directory)

    # Mode choice
    if "debug" in str(sys.argv[1:]):
        test_dir = os_control.join_dir(current_directory, "reverse_image_scraper", "tests")
        pytest.main([test_dir])  # Run all tests
    if "extract" in str(sys.argv[1:]):
        extract_images(output_dir, DEFAULT_FOLDER)
        exit()

    multi_process = True
    if "single" in str(sys.argv[1:]):
        multi_process = False
    upscale_pre_process(input_dir, current_directory, default_dir, INPUT_FOLDER, OUTPUT_FOLDER, multi_process)


def upscale_pre_process(input_dir, current_directory, default_dir, INPUT_FOLDER, OUTPUT_FOLDER, multi_process):
    """ Set up for the actual reverse image searching process. Determines how the process is done (i.e. multi-process).
    :param input_dir: Location of user-provided image files to be uploaded.
    :param current_directory: Location of the program.
    :param default_dir: Location where images go if they have no copies.
    :param INPUT_FOLDER: Name of input folder.
    :param OUTPUT_FOLDER: Name of output folder.
    :param multi_process: Boolean. Determines if search is done with one process, or multiple
    """
    files_list = os_control.list_dir(input_dir)
    if not files_list:  # Input folder is empty. Cannot progress
        print(cc.RED + cc.BOLD + "Folder: '" + input_dir + "' is empty!" + cc.RESET)
        exit()

    num_links = user_input.number_of_links(default=6, lower_bound=3, upper_bound=50)
    print(cc.GREEN + "Searching for " + str(num_links) + " copies..." + cc.RESET)

    start_time = time_now()  # Start timer

    count = 0
    img_list = []
    ext = (".jpg", ".jpeg", ".png")
    for filename in files_list:
        if filename.lower().endswith(ext):  # Only search over image files
            if multi_process:
                img_list.append(filename)
            else:
                count += upscale_image(filename, default_dir, current_directory, num_links,
                                       INPUT_FOLDER, OUTPUT_FOLDER, multi_process)

    if multi_process:
        # Loading bar set-up
        files_processed = 0
        img_list_length = len(img_list)
        loading(img_list_length, 0)

        # Run image up-scaling in parallel
        Pool = multiprocessing.Pool(processes=PROCESS)
        output_location = partial(upscale_image, default_dir=default_dir, current_directory=current_directory,
                                  num_links=num_links, INPUT_FOLDER=INPUT_FOLDER, OUTPUT_FOLDER=OUTPUT_FOLDER,
                                  multi_process=multi_process)
        for i in Pool.imap_unordered(output_location, img_list):
            files_processed += i
            loading(img_list_length, files_processed)

        # Finish timing program
        end_time = time_now()
        seconds_elapsed = end_time - start_time
        minutes, seconds = divmod(seconds_elapsed, 60)

        print(cc.YELLOW + cc.BOLD + "\nComplete!" + cc.RESET)
        print(cc.YELLOW + "Search completed in " + str(int(minutes)) + "m, " + str(int(seconds)) + "sec" + cc.RESET)
    else:
        end_time = time_now()  # Stop timer
        seconds_elapsed = end_time - start_time
        minutes, seconds = divmod(seconds_elapsed, 60)

        print(cc.YELLOW + cc.BOLD + "Complete!" + cc.RESET)
        print(cc.YELLOW + "Searched over " + str(count) + " images in "
              + str(int(minutes)) + "m, " + str(int(seconds)) + "sec" + cc.RESET)


def upscale_image(filename, default_dir, current_directory, num_links, INPUT_FOLDER, OUTPUT_FOLDER, multi_process):
    """ Uploads a file to google, and saves any larger images.
    :param filename: File to upload.
    :param default_dir: Where to put the original image if there are no larger images.
    :param current_directory: Location of the program.
    :param num_links: Max number of images to save.
    :param INPUT_FOLDER: Name of input folder.
    :param OUTPUT_FOLDER: Name of output folder.
    :param multi_process: Whether to run multi process or not.
    :return: int 1 to track completion.
    """
    # Set up
    path = os_control.join_dir(current_directory, INPUT_FOLDER, filename)  # Get path to image
    width, height = user_input.file_img_size(path)  # Save image details for comparison
    session = HTMLSession()  # Start session for web browsing
    result_url = web_control.send_image(session, path)  # Send image to google images and get URL of the results page

    # Find valid image links
    links = []  # If result_url is None, then simply move the original file to output
    if result_url is not None:
        soup = web_control.get_page_from_url(session, result_url, SoupStrainer('span', {'class', 'gl'}))  # Get HTML
        request = web_control.href_from_text(session, soup, "All sizes")  # Find relevant HREFs
        if request is not None:
            links = web_control.img_links_from_href(request, SoupStrainer('script'), num_links)  # Get list of URLs

    # Loop through image results, saving relevant images
    img_move_flag = False
    index = filename.rfind(".")  # Separate name and extension
    dir_name = filename[:index] + "(" + filename[index + 1:] + ")"  # Add file extension to name
    for link in links:  # For each link, try to save the image.
        img, web_width, web_height, err = web_control.img_size(session, link)  # Get image with dimensions
        if img is None:  # Link did not contain an image or was otherwise invalid
            to_print(multi_process, "invalid", {"link": link})
            continue

        if web_width > width or web_height > height:  # Web image must be bigger than original to be saved
            os_control.make_dir(os_control.join_dir(OUTPUT_FOLDER, dir_name), current_directory)  # Save new img here
            img_move_flag = True
            title = link.split("/")[-1]  # Use end of link as new title, and save image.
            saved_img_flag = os_control.save_image(img, os_control.join_dir(current_directory,
                                                                            OUTPUT_FOLDER, dir_name, title))

            if err == 403:  # Create note that larger image may exist but is blocked
                os_control.make_note(os_control.join_dir(current_directory, OUTPUT_FOLDER, dir_name),
                                     "Forbidden error - try manually searching.txt")
            if not saved_img_flag:  # If cannot save image, skip
                to_print(multi_process, "save", {"link": link})
                continue
            to_print(multi_process, "data", {"title": title, "web_width": web_width, "web_height": web_height})
        else:
            to_print(multi_process, "skip", {"link": link})

    # If an image has a larger match, move original file to new folder; else remove original from search
    if img_move_flag:
        source = os_control.join_dir(current_directory, INPUT_FOLDER) + "\\"
        destination = os_control.join_dir(current_directory, OUTPUT_FOLDER, dir_name) + "\\"
        os_control.move_file(filename, source, destination)
    else:
        source = os_control.join_dir(current_directory, INPUT_FOLDER) + "\\"
        destination = os_control.join_dir(current_directory, default_dir) + "\\"
        os_control.move_file(filename, source, destination)
    to_print(multi_process, "moved", {"filename": filename})
    return 1  # Increment counter


def extract_images(output_dir, DEFAULT_FOLDER):
    """ Move manually sorted files to default folder.
    :param output_dir: Location to search through.
    :param DEFAULT_FOLDER: Location to move files.
    """
    dir_list = os_control.list_dir(output_dir)  # Get list of folders from the output folder

    count = 0
    for folder in dir_list:  # Loop through folders, extracting single files from directories.
        dir_name = os_control.join_dir(output_dir, folder)
        if isdir(dir_name):  # Check folder is a directory
            if folder == DEFAULT_FOLDER:
                continue

            # If directory has a single file, move it to default folder.
            sub_dir_list = os_control.list_dir(dir_name)  # Get list of sub directories
            num_files = len(sub_dir_list)  # Count sub directories
            if num_files == 1:
                filename = sub_dir_list[0]  # Select first hit (since there should only be one)
                source = dir_name + "\\"
                destination = os_control.join_dir(output_dir, DEFAULT_FOLDER) + "\\"
                os_control.move_file(filename, source, destination)
                count += 1

            # Cleanup
            os_control.remove_empty_dir(dir_name)
    print(cc.GREEN + "Moved " + str(count) + " file(s)." + cc.RESET + "\n")
    print(cc.YELLOW + cc.BOLD + "Complete!" + cc.RESET)


def to_print(multi_process, key, data):
    """ Switch statement for choosing what to print.
    :param multi_process: Whether switch gets activated or not. Does not run when multi-threaded.
    :param key: String matching one of the dictionary keys.
    :param data: Dictionary holding any data needed for the print.
    """
    if not multi_process:
        switcher = {
            "invalid": cc.RED + "[+] Invalid image link!" + "     " + data.get("link", "DEFAULT") + cc.RESET,
            "save": cc.RED + "[+] Image failed to save:   " + data.get("link", "DEFAULT") + cc.RESET,
            "data": cc.LGREEN + "Saved image:" + cc.RESET + data.get("title", "DEFAULT") + cc.LGREEN
                    + "; width:" + cc.RESET + str(data.get("web_width", "DEFAULT")) + cc.LGREEN
                    + " height:" + cc.RESET + str(data.get("web_height", "DEFAULT")),
            "skip": cc.RED + "[+] Skipping smaller image: " + data.get("link", "DEFAULT") + cc.RESET,
            "moved": cc.LGREEN + data.get("filename", "DEFAULT") + " moved to output." + cc.RESET + "\n"
        }
        print(switcher.get(key, "Invalid key"))


def loading(total, files_processed):
    """ A progress bar
    :param total: total number of items.
    :param files_processed: current number of completed items.
    """
    sys.stdout.write('\r')
    bar_value = int(files_processed / total * 100)
    bar = ""
    for i in range(bar_value):
        bar += "█"
    for i in range(99 - bar_value):
        bar += " "
    if bar_value < 100:
        bar += "|"
    sys.stdout.write(cc.LBLUE + bar + "  " + cc.RESET
                     + str(bar_value) + "%" + " -- "
                     + "[" + str(files_processed) + "/" + str(total) + "]")
