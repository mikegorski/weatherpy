from unittest.mock import patch

import pytest
from weatherpy.ui.config import geo_coords_valid, set_units


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


# Happy path tests with various realistic test values
@pytest.mark.parametrize(
    "loc, expected",
    [
        (("0", "0"), True),
        (("45.0", "-90.0"), True),
        (("-45.0", "90.0"), True),
        (("90", "180"), True),
        (("-90", "-180"), True),
    ],
)
def test_geo_coords_valid_happy_path(loc, expected):
    # Act
    result = geo_coords_valid(loc)

    # Assert
    assert result == expected


# Edge cases
@pytest.mark.parametrize(
    "loc, expected",
    [
        (("90.0001", "0"), False),
        (("0", "180.0001"), False),
        (("-90.0001", "0"), False),
        (("0", "-180.0001"), False),
        (("90", "180"), True),
        (("-90", "-180"), True),
    ],
)
def test_geo_coords_valid_edge_cases(loc, expected):
    # Act
    result = geo_coords_valid(loc)

    # Assert
    assert result == expected


# Error cases
@pytest.mark.parametrize(
    "loc, expected",
    [
        (("not_a_number", "0"), False),
        (("0", "not_a_number"), False),
        (("not_a_number", "not_a_number"), False),
        ((None, "0"), False),
        (("0", None), False),
        (("123.456", ""), False),
        (("", "123.456"), False),
        (("123.456", " "), False),
        ((" ", "123.456"), False),
        (("123.456", "123.456.789"), False),
        (("123.456.789", "123.456"), False),
    ],
)
def test_geo_coords_valid_error_cases(loc, expected):
    # Act
    result = geo_coords_valid(loc)

    # Assert
    assert result == expected
