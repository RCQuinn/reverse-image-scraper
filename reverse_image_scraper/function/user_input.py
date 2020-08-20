# Third party imports
from PIL import Image


def number_of_links():
    """ Asks user for a limit to how many links to search for.
    :return: A valid number.
    """
    DEFAULT = 6
    LOWER_BOUND = 3
    UPPER_BOUND = 50

    user_input = input("How many image links to attempt? Defaults to " + str(DEFAULT) + ".\n")
    try:
        num = int(user_input)  # Try to convert user input into integer
    except (ValueError, TypeError):  # Input is NOT an integer
        num = DEFAULT  # Use default value instead of input

    # Restrict to bounds
    if num < LOWER_BOUND:  # Too few searches have high likelihood of missing hits
        num = LOWER_BOUND
    elif num > UPPER_BOUND:  # If the search hasn't found it by this point, it probably doesn't exist
        num = UPPER_BOUND

    return num


def file_img_size(path):
    """ Get dimensions of user provided images.
    :param path: Location of image.
    :return: Width and height of an image.
    """
    img = Image.open(path)
    width, height = img.size  # Save relevant data
    img.close()
    return width, height
