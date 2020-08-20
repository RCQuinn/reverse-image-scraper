# Standard library imports
import re
from io import BytesIO

# Third party imports
from bs4 import BeautifulSoup
from PIL.Image import DecompressionBombError
from PIL import Image, UnidentifiedImageError
from requests.exceptions import ConnectionError

# Local imports
from ..common.colors import ColorCodes as cc


def send_image(session, path):
    """ Takes a image saved on file, uploads it to google images, and saves the resulting URL.
    :param session: HTML session to access the internet.
    :param path: Location of image on file.
    :return: Header URL of the resulting web page, or None if the image is too large.
    """
    try:
        # Destination URL
        url = "http://www.google.com/searchbyimage/upload"

        # Send binary data to url
        multipart = {'encoded_image': (path, open(path, 'rb')), 'image_content': ''}
        request = session.post(url, files=multipart, allow_redirects=False)

        # Get the new destination url
        try:
            fetchUrl = str(request.headers['Location'])
        except KeyError:
            # Image is too large to upload.
            if request.status_code == 413:
                return None
            else:
                raise
        return fetchUrl
    except ConnectionError:
        print(cc.RED + cc.BOLD + "Error: No connection!" + cc.RESET)
        exit()


def request_to_bs4(strainer, request):
    """ Converts a HTML page to a BeautifulSoup object.
    :param strainer: Restriction on what elements should be found.
    :param request: Source of the HTML page.
    :return: BeautifulSoup object.
    """
    # Convert request to BeautifulSoup object, with or without strainer restrictions.
    if strainer:
        soup = BeautifulSoup(request.text, "lxml", parse_only=strainer)
    else:
        soup = BeautifulSoup(request.text, "lxml")
    return soup


def get_page_from_url(session, url, strainer=None):
    """ Renders a web page, including the javascript.
    :param session: HTML session to access the internet.
    :param url: Web address to page.
    :param strainer: Restriction on what elements should be found.
    :return: BeautifulSoup object.
    """
    request = session.get(url)
    request.html.render()
    soup = request_to_bs4(strainer, request)
    return soup


def href_from_text(session, soup, text):
    """ Find a href parent from some text in HTML
    :param session: HTML session to access the internet.
    :param soup: BeautifulSoup object.
    :param text: String to search for.
    :return: URL to web page, or None if nothing exists.
    """
    find_text = soup.find(text=text)  # Get the BeautifulSoup object for the first instance of 'text'
    try:
        find_href = str(find_text.parent.get("href"))  # Find the href parent of the text.
        url = "https://www.google.com" + find_href.replace("amp;", "")  # Fix abstracted url to be use-able.
    except AttributeError:  # The text may not exist in the soup, or exist at all.
        return None
    else:
        try:
            request = session.get(url)
            request.html.render()  # Get the requests page, loading javascript
        except ConnectionError:  # Empty 'text' value causes failed url
            return None
        return request


def img_links_from_href(request, strainer, num_links):
    """ Find all URLs that end in a image extension
    :param request: Source of the HTML page.
    :param strainer: Restriction on what elements should be found.
    :param num_links: Limit on the number of links to be returned.
    :return: A list of URLs
    """
    soup = request_to_bs4(strainer, request)
    soup_str = str(soup)  # Convert soup to string

    # Gets any link that ends in an image format. Rejects any link that contains a: \ [ ] { } < > %
    snipped = re.findall('http[^\\\\\\[\\]{}<>%]*\\.(?:jpg|jpeg|png)', soup_str, re.IGNORECASE)
    return snipped[:num_links]  # Return limited number of results.


def img_size(session, url):
    """ Get image size from a web image
    :param session: HTML session to access the internet.
    :param url: Address of the image.
    :return: The image itself, height, width, and any special errors. Returns None and -1 on error.
    """
    err = None
    try:
        # Get status code
        request = session.get(url)
        if request.status_code == 403:
            err = 403

        data = session.get(url).content
        img = Image.open(BytesIO(data))
        width, height = img.size
        return img, width, height, err
    except (UnidentifiedImageError, ConnectionError, DecompressionBombError):
        return None, -1, -1, err
