# Third party imports
import pytest
from unittest import mock

# Local imports
from ..function import user_input


def run_all():
    test_user_num_links_valid_input()


def test_user_num_links_valid_input():  # TODO Remove?
    with mock.patch('builtins.input', return_value=10):
        assert user_input.number_of_links() == 10

