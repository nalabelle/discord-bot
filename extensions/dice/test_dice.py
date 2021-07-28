"""
Test Dice
"""

import re

import pytest

from .dice import Dice, Roll


def test_roll_1d1():
    roll = Roll("1d1")
    assert roll.score == 1
    assert roll.explain == "[1]"


def test_roll_complex():
    roll = Roll("1d6 + 1d4 - 2")
    assert roll.score >= 0
    assert roll.score <= 8
    explain = roll.explain
    assert explain
    explain_regex = r"^\[[1-6]\] \+ \[[1-4]\] - 2$"
    assert re.match(explain_regex, explain)


@pytest.mark.asyncio
async def test_command_roll():
    dice_command = Dice(None)

    result = dice_command._roll(phrase="1d1")  # pylint: disable=protected-access
    expected_content = "Result: {} `{}`".format(1, "[1]")
    assert result == expected_content
