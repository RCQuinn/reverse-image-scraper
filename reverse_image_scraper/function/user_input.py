# Third party imports
from PIL import Image


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

    if num < 0:     # Make sure bounds don't push the value into negatives.
        num = 0

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
