# Third party imports
from PIL import Image

# Local imports
from ..common.colors import ColorCodes as cc


def number_of_links(default, lower_bound, upper_bound):
    """ Asks user for a limit to how many links to search for.
    :return: A valid number.
    """
    user_input = input("How many image links to attempt? Defaults to " + str(default) + ".\n")
    try:
        num = int(user_input)  # Try to convert user input into integer
    except (ValueError, TypeError):  # Input is NOT an integer
        num = default  # Use default value instead of input

    # Restrict to bounds
    if num < lower_bound:  # Too few searches have high likelihood of missing hits
        num = lower_bound
    elif num > upper_bound:  # If the search hasn't found it by this point, it probably doesn't exist
        num = upper_bound

    if lower_bound < 0 or upper_bound < 0:     # There should never be negative bounds.
        print(cc.RED + "\nNegative bounds are invalid! Try again." + cc.RESET)
        exit()
    if lower_bound > upper_bound:              # Lower should never be greater than upper
        print(cc.RED + "\nLower bound is greater than upper bound! Try again." + cc.RESET)
        exit()

    return num


def file_img_size(abs_path):
    """ Get dimensions of user provided images.
    :param abs_path: Absolute path of image location.
    :return: Width and height of an image.
    """
    img = Image.open(abs_path)
    width, height = img.size  # Save relevant data
    img.close()
    return width, height
