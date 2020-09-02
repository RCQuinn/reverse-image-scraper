# Standard library imports
from unittest import mock
from unittest.mock import patch

# Third party imports
import pytest

# Local imports
from ..function import user_input


@pytest.mark.parametrize(
    "default, lower_bound, upper_bound, test_input, expected_output",
    [
        (6, 3, 50,   10, 10),       # 10 fits between 3-50, so return same value(10).
        (6, 3, 50,   0, 3),         # 0 is below 3-50, so return lower_bound(3)
        (6, 3, 50,   100, 50),      # 100 is above 3-50, so return upper_bound(50)
        (6, 3, 50,   None, 6),      # None is not a value, so return default(6)
        (6, 3, 50,   [], 6),        # [] is not a value, so return default(6)
        (6, 3, 50,   "", 6),        # "" is not a value, so return default(6)
        (6, 3, 50,   '\n', 6),      # '\n' is not a value, so return default(6)
        (6, 3, 50,   "\\\\", 6),    # "\\\\" is not a value, so return default(6)
        (6, 3, 50,   True, 3),      # Boolean acts as value(1), return lower_bound(3)
        (6, 3, 50,   10.5, 10),     # Fraction not supported, return truncated(10)
        (6, 3, 50,   "ٱلْعَرَبِيَّة‎", 6),    # r-to-l text is not a value, return default(6)
                                    # 1 googol is above 3-50, return upper bound(50)
        (6, 3, 50,   10000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000, 50),  # noqa
                                    # Long fraction gets shortened, then truncated, so return(10)
        (6, 3, 50,   10.5555555555555555555555555555555555555555555555555555555555555555555555555555555555555555555555555555, 10)  # noqa
    ]
)
def test_number_of_links__returns_correct_values(default, lower_bound, upper_bound, test_input, expected_output):
    with mock.patch('builtins.input', return_value=test_input):
        assert user_input.number_of_links(default, lower_bound, upper_bound) == expected_output


def test_number_of_links__throws_SystemExit_on_invalid_bounds():
    with mock.patch('builtins.input', return_value=10):
        with pytest.raises(SystemExit):
            user_input.number_of_links(3, -10, -5)
        with pytest.raises(SystemExit):
            user_input.number_of_links(3, 10, 5)


@patch(user_input.__name__ + ".Image")
def test_file_img_size__returns_expected_dimensions(mock_image):
    opened_image = mock_image.open.return_value
    opened_image.size = (42, 83)

    width, height = user_input.file_img_size("a/dir/test.jpg")

    mock_image.open.assert_called_once_with('a/dir/test.jpg')       # Test directory called correctly.
    mock_image.open.return_value.close.assert_called_once_with()    # Test call to close image is run.
    assert width == 42 and height == 83                             # Test values are as expected
