# Standard library imports
from unittest.mock import patch

# Third party imports
import pytest

# Local imports
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

# TODO see if it can auto generate 'assert_not_called' for an empty input
def test_remove_empty_dir(mocker):
    # Arrange: Auto generated
    mock_os = mocker.MagicMock(name='os')
    mocker.patch('reverse_image_scraper.function.os_control.os', new=mock_os)

    # Act: invoke test code
    os_control.remove_empty_dir("/a/dir")

    # Assert: Auto generated
    mock_os.listdir.assert_called_once_with('/a/dir')
    mock_os.listdir.return_value.__len__.assert_called_once_with()
    mock_os.rmdir.assert_called_once_with('/a/dir')

# TODO
#def test_get_main_dir():
#    assert os_control.get_main_dir()[-21:] == "reverse_image_scraper"  # Test directory ends in expected name


@pytest.mark.parametrize(
    "test_input, expected_output",
    [
        ("\\foo\\bar\\far\\boo", "\\\\?\\"),  # Test directory starting with \
        ("foo\\bar\\far\\boo", "\\\\?\\")  # Test direction missing \
    ]
)
def test_exceed_NTFS_file_limit(test_input, expected_output):
    assert os_control.exceed_NTFS_file_limit(test_input)[:4] == expected_output


def test_join_dir():
    assert os_control.join_dir("", "") == ""  # Shouldn't combine empty entries
    assert os_control.join_dir("a", "", "b", "c", "d", "e", "f", "g") == "a\\b\\c\\d\\e\\f\\g"  # Combines many


@patch(os_control.__name__ + ".os.listdir")
def test_list_dir(mock_list_dir):
    mock_list_dir.return_value = ["dir_one", "dir_two"]
    result = os_control.list_dir("a_dir")
    assert result == ["dir_one", "dir_two"]
    mock_list_dir.assert_called_once_with("a_dir")


def test_list_dir_throws_FileNotFoundError():
    with pytest.raises(FileNotFoundError):
        os_control.list_dir("ThisDirectoryShouldn'tPossiblyExistAsItIsFarTooLongForAnybodyToReasonablyMakeThis_31415")


@patch(os_control.__name__ + ".os.listdir")
@patch(os_control.__name__ + ".os.rmdir")
def test_remove_empty_dir(mock_rmdir, mock_list_dir):
    mock_list_dir.return_value = []
    os_control.remove_empty_dir("a_dir")
    mock_rmdir.assert_called_once_with("a_dir")


@patch(os_control.__name__ + ".os.listdir")
@patch(os_control.__name__ + ".os.rmdir")
def test_remove_empty_dir_fails_on_non_empty_dir(mock_rmdir, mock_list_dir):
    mock_list_dir.return_value = ["dir_one", "dir_two"]
    os_control.remove_empty_dir("a_dir")
    mock_rmdir.assert_not_called()


@patch(os_control.__name__ + ".open")
def test_make_note(mock_open):
    os_control.make_note("a_dir", "a_title")
    mock_open.assert_called_once_with("a_dir\\a_title", "a+")



