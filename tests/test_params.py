# SPDX-License-Identifier: GPL-3.0-or-later
import pytest

from params import PARAMETER_TYPES, parse_value


@pytest.mark.parametrize(
    ("ptype", "text", "expected"),
    [
        ("number", "0.25", 0.25),
        ("number", "", 0.0),
        ("integer", "7", 7),
        ("integer", "7.0", 7),
        ("toggle", "TRUE", True),
        ("toggle", "no", False),
        ("text", " a ", " a "),
        ("prompt", "a cat", "a cat"),
        ("choice", "euler", "euler"),
    ],
)
def test_parse_value(ptype, text, expected):
    assert parse_value(ptype, text) == expected


def test_unknown_type():
    with pytest.raises(ValueError, match="unknown"):
        parse_value("colour", "red")


def test_types_are_stable():
    assert PARAMETER_TYPES == ("number", "integer", "toggle", "text", "prompt", "choice")
