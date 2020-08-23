# Third party imports
import pytest
from unittest import mock

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
        (6, 3, 50,   10.5555555555555555555555555555555555555555555555555555555555555555555555555555555555555555555555555555, 10),  # noqa
        (6, -9, 50,  -1, 0)         # Return value can never be negative, so return 0
    ]
)
def test_number_of_links(default, lower_bound, upper_bound, test_input, expected_output):
    with mock.patch('builtins.input', return_value=test_input):
        assert user_input.number_of_links(default, lower_bound, upper_bound) == expected_output

