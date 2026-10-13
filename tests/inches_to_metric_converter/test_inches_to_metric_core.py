"""Headless tests of the conversion core, written from the acceptance criteria."""
from decimal import Decimal, ROUND_HALF_UP
from itertools import permutations

import pytest

from inches_to_metric_converter.core import (
    UNITS,
    InvalidNumberError,
    NonPositiveValueError,
    convert,
    convert_text,
)

EXPECTED_UNITS = (
    "millimeters", "centimeters", "meters", "kilometers",
    "inches", "feet", "yards", "miles",
)

# Factors taken from the requirements' Assumptions (independent of the code).
ASSUMED_METERS_PER_UNIT = {
    "millimeters": Decimal("0.001"),
    "centimeters": Decimal("0.01"),
    "meters": Decimal("1"),
    "kilometers": Decimal("1000"),
    "inches": Decimal("0.0254"),
    "feet": Decimal("0.3048"),
    "yards": Decimal("0.9144"),
    "miles": Decimal("1609.344"),
}

MSG_NOT_POSITIVE = "Please enter a number greater than zero."
MSG_INVALID = "Please enter a valid number."


# REQ-002 / REQ-003: unit lists (headless, via core.UNITS)
def test_req_002_from_units_list_order():
    assert tuple(UNITS) == EXPECTED_UNITS


def test_req_003_to_units_list_order():
    assert tuple(UNITS) == EXPECTED_UNITS
    assert len(UNITS) == 8


# REQ-004: conversions between different units
@pytest.mark.parametrize(
    "value, from_unit, to_unit, expected",
    [
        ("1", "inches", "millimeters", "25.40"),       # AC-1
        ("1", "miles", "kilometers", "1.61"),          # AC-2
        ("1", "meters", "feet", "3.28"),               # AC-3
        ("1", "yards", "meters", "0.91"),              # AC-4
        ("1", "kilometers", "miles", "0.62"),          # AC-5
        ("1", "inches", "centimeters", "2.54"),        # AC-6
        ("1", "kilometers", "meters", "1000.00"),      # AC-7
        ("10", "centimeters", "millimeters", "100.00"),  # AC-8
        ("1", "feet", "inches", "12.00"),              # AC-9
        ("1", "miles", "yards", "1760.00"),            # AC-10
        ("1", "miles", "feet", "5280.00"),             # AC-11
        ("1", "kilometers", "feet", "3280.84"),        # AC-12
        ("2.5", "feet", "inches", "30.00"),            # AC-13
    ],
)
def test_req_004_specific_conversions(value, from_unit, to_unit, expected):
    assert str(convert(value, from_unit, to_unit)) == expected
    assert convert_text(value, from_unit, to_unit) == expected


def test_req_004_all_56_pairs_match_assumed_factors():
    pairs = list(permutations(EXPECTED_UNITS, 2))
    assert len(pairs) == 56
    for from_unit, to_unit in pairs:
        expected = (
            Decimal(1) * ASSUMED_METERS_PER_UNIT[from_unit]
            / ASSUMED_METERS_PER_UNIT[to_unit]
        ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        result = convert(1, from_unit, to_unit)
        assert result == expected, (from_unit, to_unit)
        assert convert_text("1", from_unit, to_unit) == format(expected, "f")


# REQ-005: unit to itself
def test_req_005_meters_to_meters():
    assert str(convert("7", "meters", "meters")) == "7.00"
    assert convert_text("7", "meters", "meters") == "7.00"


def test_req_005_inches_to_inches_rounds():
    assert str(convert("3.14159", "inches", "inches")) == "3.14"
    assert convert_text("3.14159", "inches", "inches") == "3.14"


@pytest.mark.parametrize("unit", EXPECTED_UNITS)
def test_req_005_each_unit_to_itself_is_one(unit):
    assert convert_text("1", unit, unit) == "1.00"


# REQ-006: display string has exactly 2 decimals
@pytest.mark.parametrize(
    "value, from_unit, to_unit, expected",
    [
        ("1", "meters", "inches", "39.37"),
        ("5", "meters", "meters", "5.00"),
        ("100", "feet", "meters", "30.48"),
        ("1", "millimeters", "miles", "0.00"),
    ],
)
def test_req_006_display_two_decimals(value, from_unit, to_unit, expected):
    assert convert_text(value, from_unit, to_unit) == expected


# REQ-007: reject zero
@pytest.mark.parametrize("text", ["0", "0.0"])
def test_req_007_zero_text_shows_message(text):
    assert convert_text(text, "inches", "millimeters") == MSG_NOT_POSITIVE


def test_req_007_convert_zero_raises():
    with pytest.raises(NonPositiveValueError) as info:
        convert(0, "inches", "millimeters")
    assert info.value.message == MSG_NOT_POSITIVE


# REQ-008: reject negatives
@pytest.mark.parametrize("text", ["-5", "-0.01"])
def test_req_008_negative_text_shows_message(text):
    assert convert_text(text, "meters", "feet") == MSG_NOT_POSITIVE


def test_req_008_convert_negative_raises():
    with pytest.raises(NonPositiveValueError) as info:
        convert(-1, "meters", "feet")
    assert info.value.message == MSG_NOT_POSITIVE


# REQ-009: reject empty / non-numeric
@pytest.mark.parametrize("text", ["", "abc", "12ft"])
def test_req_009_invalid_text_shows_message(text):
    assert convert_text(text, "inches", "millimeters") == MSG_INVALID


def test_req_009_convert_invalid_raises():
    with pytest.raises(InvalidNumberError) as info:
        convert("abc", "inches", "millimeters")
    assert info.value.message == MSG_INVALID


# REQ-006 + Assumption "Rounding to 2 decimal places rounds half up".
# Every input lands exactly on a half cent. Expected values computed by hand.
# Round-half-even would give the value in the trailing comment, so these
# cases fail if the code ever switches rounding modes.
@pytest.mark.parametrize(
    "value, from_unit, to_unit, expected",
    [
        ("1.005", "meters", "meters", "1.01"),            # half-even: 1.00
        ("2.345", "meters", "meters", "2.35"),            # half-even: 2.34
        ("1.25", "millimeters", "centimeters", "0.13"),   # 0.125 cm; half-even: 0.12
        ("0.005", "meters", "meters", "0.01"),            # half-even: 0.00
    ],
)
def test_req_006_rounds_half_up(value, from_unit, to_unit, expected):
    assert convert_text(value, from_unit, to_unit) == expected


# REQ-004 + Assumption "Surrounding spaces are ignored".
# The design's parse_amount uses str.strip(), which strips all surrounding
# whitespace (spaces, tabs, newlines), so tabs are expected to be ignored too.
@pytest.mark.parametrize(
    "text",
    [" 2.5 ", "   2.5", "2.5   ", "\t2.5\t", " \t2.5 \n"],
)
def test_req_004_ignores_surrounding_spaces(text):
    assert convert_text(text, "feet", "inches") == "30.00"


# REQ-009 + whitespace assumption: spaces do not make an invalid entry valid,
# and an entry of only spaces counts as empty.
@pytest.mark.parametrize("text", [" abc ", "  12ft  ", "   ", "\t"])
def test_req_009_invalid_with_surrounding_spaces_shows_message(text):
    assert convert_text(text, "inches", "millimeters") == MSG_INVALID


# REQ-007 / REQ-008 + whitespace assumption: zero or negative surrounded by
# spaces still gets the greater-than-zero message.
@pytest.mark.parametrize("text", [" 0 ", "\t0.0\t", " -5 "])
def test_req_007_zero_or_negative_with_surrounding_spaces_shows_message(text):
    assert convert_text(text, "inches", "millimeters") == MSG_NOT_POSITIVE
