# Standard library imports
from unittest.mock import patch

# Third-part imports
import pytest
from bs4 import BeautifulSoup
from requests_html import HTMLSession
from PIL.Image import DecompressionBombError
from PIL import Image, UnidentifiedImageError
from requests.exceptions import ConnectionError

# Local imports
from ..function import web_control


@patch(web_control.__name__ + ".open")
def test_send_image__succeed_send(mock_open):
    session = HTMLSession()
    mock_open.return_value = "rb"

    with patch.object(session, 'post') as mock_session:
        mock_session.return_value.headers.__getitem__.return_value = "www.header@url.com"
        header = web_control.send_image(session, "/a/dir/img.png")

    assert header == "www.header@url.com"                                               # Test return is valid
    mock_open.assert_called_once_with('/a/dir/img.png', 'rb')                           # Test open calls correctly
    mock_session.assert_called_once_with('http://www.google.com/searchbyimage/upload',  # Test session posts correctly
                                         allow_redirects=False,
                                         files={'encoded_image': ('/a/dir/img.png', 'rb'), 'image_content': ''})
    mock_session.return_value.headers.__getitem__.assert_called_once_with('Location')   # Test header finds correctly


@patch(web_control.__name__ + ".open")
def test_send_image__fail_send(mock_open):
    session = HTMLSession()
    mock_open.return_value = "rb"

    with patch.object(session, 'post') as mock_session:
        mock_session.return_value.headers.__getitem__.side_effect = KeyError
        mock_session.return_value.status_code = 413
        header = web_control.send_image(session, "/a/dir/img.png")

    assert header is None                                                               # Test return is invalid
    mock_open.assert_called_once_with('/a/dir/img.png', 'rb')                           # Test open calls correctly


@patch(web_control.__name__ + ".open")
def test_send_image__closes_on_no_connection(mock_open):
    session = HTMLSession()

    with patch.object(session, 'post') as mock_session:
        mock_session.side_effect = ConnectionError
        with pytest.raises(SystemExit):  # Test closes gracefully
            web_control.send_image(session, "/a/dir/img.png")

    mock_open.assert_called_once_with('/a/dir/img.png', 'rb')  # Test open calls correctly


@patch(web_control.__name__ + ".BeautifulSoup")
def test_request_to_bs4__strainer_exists(mock_soup):
    session = HTMLSession()
    with patch.object(session, 'request') as mock_session:
        mock_session.return_value.text = "some_HTML_code"
        web_control.request_to_bs4("strainer", session.request("method", "http://url"))

    mock_soup.assert_called_once_with("some_HTML_code", "lxml", parse_only="strainer")


@patch(web_control.__name__ + ".BeautifulSoup")
def test_request_to_bs4__strainer_missing(mock_soup):
    session = HTMLSession()
    with patch.object(session, 'request') as mock_session:
        mock_session.return_value.text = "some_HTML_code"
        web_control.request_to_bs4(None, session.request("method", "http://url"))

    mock_soup.assert_called_once_with("some_HTML_code", "lxml")


@patch(web_control.__name__ + ".BeautifulSoup")
def test_page_from_url__succeeds(mock_soup):
    session = HTMLSession()
    with patch.object(session, 'request') as mock_session:
        mock_session.return_value.text = "some_HTML_code"
        web_control.get_page_from_url(session, "http://url", )

    mock_session.assert_called_once_with('GET', 'http://url', allow_redirects=True)
    mock_session.return_value.html.render.assert_called_once_with()
    mock_soup.assert_called_once_with('some_HTML_code', 'lxml')


def test_href_from_text__succeed_return():
    session = HTMLSession()
    soup = BeautifulSoup("some_HTML_code", "lxml")
    with patch.object(session, 'request') as mock_session:
        with patch.object(soup, "find") as mock_soup:
            mock_soup.return_value.parent.get.return_value = "/some/url/ending"
            request = web_control.href_from_text(session, soup, "text")

    assert request is not None
    mock_soup.assert_called_once_with(text='text')
    mock_soup.return_value.parent.get.assert_called_once_with('href')
    mock_session.assert_called_once_with('GET', 'https://www.google.com/some/url/ending', allow_redirects=True)
    mock_session.return_value.html.render.assert_called_once_with()


def test_href_from_text__AttributeError_returns_none():
    session = HTMLSession()
    soup = BeautifulSoup("some_HTML_code", "lxml")
    with patch.object(session, 'request') as mock_session:
        with patch.object(soup, "find") as mock_soup:
            mock_soup.return_value.parent.get.side_effect = AttributeError
            request = web_control.href_from_text(session, soup, "text")

    assert request is None
    mock_session.assert_not_called()
    mock_soup.assert_called_once_with(text='text')
    mock_soup.return_value.parent.get.assert_called_once_with('href')


def test_href_from_text__empty_text_returns_none():
    session = HTMLSession()
    soup = BeautifulSoup("some_HTML_code", "lxml")

    with patch.object(session, 'request') as mock_session:
        request = web_control.href_from_text(session, soup, "")

    assert request is None
    mock_session.assert_not_called()


@pytest.mark.parametrize(
    "soup, expected_output",
    [
        ("https://img.web.com/photo-150.jpg", "https://img.web.com/photo-150.jpg"),
        ("https://img.web.com/photo-150.PNG", "https://img.web.com/photo-150.PNG"),
        ("https://img.web.com/photo-150.jpeg", "https://img.web.com/photo-150.jpeg"),
        ("http://img.web.com.au.gov.net.nz.co/photo-150.jpg", "http://img.web.com.au.gov.net.nz.co/photo-150.jpg"),
        ("[<https://img.web.com/photo-150.jpg.[][][].jpg>]", "https://img.web.com/photo-150.jpg"),
        ("[https://\\\\1231!!2!@#534@#<https://img.web.com/photo-150.jpg.[][][].jpg>].jpg!!32#%#$.pngjpg",
         "https://img.web.com/photo-150.jpg"),
    ]
)
def test_img_links_from_href__valid_urls(soup, expected_output):
    with patch(web_control.__name__ + ".request_to_bs4") as mock_bs4_function:
        mock_bs4_function.return_value = soup
        lst = web_control.img_links_from_href(soup, "strainer", 10)

    assert lst[0] == expected_output


@pytest.mark.parametrize(
    "soup",
    [
        "https:\\\\img.web.com/photo-150.jpg",
        "https://img.web.{com}/photo-150.jpg",
        "https://img.web.[com]/photo150.jpg",
        "https://img.web.<com>/photo-150.jpg",
        "https://img.web.com%/photo-150.jpg",       # '%' can introduce unnecessary data
    ]
)
def test_img_links_from_href__invalid_urls(soup):
    with patch(web_control.__name__ + ".request_to_bs4") as mock_bs4_function:
        mock_bs4_function.return_value = soup
        lst = web_control.img_links_from_href(soup, "strainer", 10)

    assert not lst


@patch(web_control.__name__ + ".BytesIO")
@patch(web_control.__name__ + ".Image.open")
def test_img_size__succeeds(mock_Image, mock_bytes):
    session = HTMLSession()
    image = Image.new(mode="RGB", size=(200, 200))
    image.format = "png"

    with patch.object(session, "get") as mock_session:
        mock_Image.return_value = image
        mock_session.return_value.content = "page_data"
        mock_session.return_value.status_code = 403

        img, width, height, err = web_control.img_size(session, "https://url.com")

    assert img is image and width == 200 and height == 200 and err == 403       # Test return value is as expected
    mock_bytes.assert_called_once_with('page_data')                             # Test page data is passed to BytesIO
    mock_session.assert_called_once_with('https://url.com')                     # Test session gets url


@patch(web_control.__name__ + ".BytesIO")
@patch(web_control.__name__ + ".Image.open")
def test_img_size__fails(mock_Image, mock_bytes):
    session = HTMLSession()

    # Web error
    with patch.object(session, "get") as mock_session:
        mock_session.side_effect = ConnectionError
        img, width, height, err = web_control.img_size(session, "https://url.com")
    assert img is None and width == -1 and height == -1 and err is None

    # Image errors
    with patch.object(session, "get"):
        mock_Image.side_effect = UnidentifiedImageError
        img, width, height, err = web_control.img_size(session, "https://url.com")
    assert img is None and width == -1 and height == -1 and err is None
    with patch.object(session, "get"):
        mock_Image.side_effect = DecompressionBombError
        img, width, height, err = web_control.img_size(session, "https://url.com")
    assert img is None and width == -1 and height == -1 and err is None
    assert 2 == mock_bytes.call_count   # Test the above two errors call BytesIO
