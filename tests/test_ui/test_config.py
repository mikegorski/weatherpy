from unittest.mock import patch

import pytest
from weatherpy.ui.config import set_units


@pytest.mark.parametrize(
    "user_input, expected_output",
    [
        ("m", "metric"),
        ("i", "imperial"),
        ("s", "standard"),
    ],
)
def test_set_units_should_return_correct_value_per_user_input(user_input, expected_output):
    with patch("rich.prompt.Prompt.ask", return_value=user_input):
        result = set_units()
        assert result == expected_output, f"Test failed for {user_input = }."
