# Standard library imports
from unittest.mock import patch, call

# Third party imports
import PIL
import pytest

# Local imports
from PIL import Image

from ..function import os_control

# EXAMPLE AUTO TEST
# https://medium.com/datadriveninvestor/mocking-python-like-a-boss-65377d943c20
# Def test(mocker):
#   # Arrange - replace below with resulting print
#   from mock_autogen.pytest_mocker import PytestMocker
#   print(PytestMocker(zip_writer).mock_modules().generate())
#
#   # Act. Call the function to test
#   function.to_test("test_string")
#
#   # Assert
#   import mock_autogen.generator
#   generated_asserts = mock_autogen.generator.generate_asserts(mock_zipfile)
#   print("\n")
#   print(generated_asserts)


def test_get_main_dir__returns_expected_folder_name():
    assert os_control.get_main_dir()[-25:] == "reverse_image_scraper_git"  # Test directory ends in expected name


@pytest.mark.parametrize(
    "test_input, expected_output",
    [
        ("\\foo\\bar\\far\\boo", "\\\\?\\"),  # Test directory starting with \
        ("foo\\bar\\far\\boo", "\\\\?\\")  # Test direction missing \
    ]
)
def test_exceed_NTFS_file_limit__returns_expected_prefix(test_input, expected_output):
    assert os_control.exceed_NTFS_file_limit(test_input)[:4] == expected_output


def test_join_dir__returns_expected_combinations():
    assert os_control.join_dir("", "") == ""  # Shouldn't combine empty entries
    assert os_control.join_dir("a", "", "b", "c", "d", "e", "f", "g") == "a\\b\\c\\d\\e\\f\\g"  # Combines many


@patch(os_control.__name__ + ".os.listdir")
def test_list_dir__returns_expected_list(mock_list_dir):
    mock_list_dir.return_value = ["dir_one", "dir_two"]

    result = os_control.list_dir("a_dir")

    assert result == ["dir_one", "dir_two"]
    mock_list_dir.assert_called_once_with("a_dir")


@patch(os_control.__name__ + ".os")
def test_remove_empty_dir__removes_if_empty(mock_os):
    mock_os.listdir.return_value = []

    os_control.remove_empty_dir("/a/dir/")

    mock_os.listdir.assert_called_once_with("/a/dir/")
    mock_os.rmdir.assert_called_once_with("/a/dir/")


@patch(os_control.__name__ + ".os")
def test_remove_empty_dir__keeps_if_not_empty(mock_os):
    mock_os.listdir.return_value = ["dir_one", "dir_two"]

    os_control.remove_empty_dir("a_dir")

    mock_os.listdir.assert_called_once_with('a_dir')
    mock_os.rmdir.assert_not_called()


@patch(os_control.__name__ + ".open")
def test_make_note__creates_expected_file(mock_open):
    os_control.make_note("a_dir", "a_title")

    assert 1 == mock_open.call_count
    mock_open.assert_called_once_with('a_dir\\a_title', 'a+')
    mock_open.return_value.close.assert_called_once_with()


def test_save_image__succeeds_saving():
    image = PIL.Image.new(mode="RGB", size=(200, 200))
    image.format = "png"

    with patch.object(image, 'save') as mock_save:
        with patch.object(image, 'close') as mock_close:
            save_flag = os_control.save_image(image, "/a/dir/")

    mock_save.assert_called_once_with('/a/dir/', "png")         # Test image is as expected
    mock_close.assert_called_once_with()                        # Test image closes
    assert save_flag is True                                    # Test method returns correct value


def test_save_image__fails_saving():
    image = PIL.Image.new(mode="RGB", size=(200, 200))
    image.format = "png"

    with patch.object(image, 'save', side_effect=OSError) as mock_save:
        with patch.object(image, 'close') as mock_close:
            save_flag = os_control.save_image(image, "/a/dir/")

    assert 10 == mock_save.call_count                           # Tests the save attempts occur as expected
    mock_close.assert_called_once_with()                        # Test image closes
    assert save_flag is False                                   # Test method returns correct value"""


@patch(os_control.__name__ + ".os.makedirs")
@patch(os_control.__name__ + ".os.path.exists")
def test_make_dir__succeeds_making(mock_path_exists, mock_makedirs):
    mock_path_exists.return_value = False

    os_control.make_dir("name", "\\a\\dir\\")

    mock_makedirs.assert_called_once_with("\\a\\dir\\name")


@patch(os_control.__name__ + ".os.makedirs")
@patch(os_control.__name__ + ".os.path.exists")
def test_make_dir__fails_making(mock_path_exists, mock_makedirs):
    mock_path_exists.return_value = True

    os_control.make_dir("name", "\\a\\dir\\")

    mock_makedirs.assert_not_called()


@patch(os_control.__name__ + ".os.makedirs")
@patch(os_control.__name__ + ".os.path.exists")
def test_make_dir__throws_SystemExit(mock_path_exists, mock_makedirs):
    mock_path_exists.return_value = False
    mock_makedirs.side_effect = OSError

    with pytest.raises(SystemExit):
        os_control.make_dir("name", "\\a\\dir\\")


@patch(os_control.__name__ + ".os.rename")
def test_move_file__succeeds_move(mock_rename):
    os_control.move_file("name", "/a/source/", "/a/destination/")

    mock_rename.assert_called_once_with('/a/source/name', '/a/destination/name')


@patch(os_control.__name__ + ".os.rename")
def test_move_file__fails_move(mock_rename):
    mock_rename.side_effect = [FileExistsError, FileExistsError, FileExistsError, None]  # Simulates three files exist

    os_control.move_file("name.txt", "/a/source/", "/a/destination/")

    calls = [
        call("/a/source/name.txt", "/a/destination/name.txt"),
        call("/a/source/name.txt", "/a/destination/name(1).txt"),
        call("/a/source/name.txt", "/a/destination/name(2).txt"),
        call("/a/source/name.txt", "/a/destination/name(3).txt")
    ]
    assert mock_rename.call_args_list == calls







