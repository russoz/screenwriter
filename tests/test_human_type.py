# (C) 2025 Alexei Znamensky
# Licensed under the GPL-3.0-or-later license. See LICENSES/GPL-3.0-or-later.txt for details.
# SPDX-FileCopyrightText: 2025 Alexei Znamensky
# SPDX-License-Identifier: GPL-3.0-or-later
from asciinwriter.__main__ import AsciinwriterRunner


def test_human_type_sends_characters(mocker):
    """Test that human_type sends each character with delays."""
    runner = AsciinwriterRunner(
        typing_delay_range=(0.05, 0.05), jitter_factor=0, post_typing_delay=0.1
    )
    mock_sleep = mocker.patch("asciinwriter.__main__.time.sleep")
    mock_child = mocker.Mock()

    runner.human_type(mock_child, "hello")

    # Should call send for each character
    assert mock_child.send.call_count == 5
    mock_child.send.assert_any_call("h")
    mock_child.send.assert_any_call("e")
    mock_child.send.assert_any_call("l")
    mock_child.send.assert_any_call("l")
    mock_child.send.assert_any_call("o")

    # Should sleep between each character plus final delay
    assert mock_sleep.call_count == 6  # 5 chars + 1 final delay


def test_human_type_prints_output(mocker):
    """Test that human_type prints characters to stdout."""
    runner = AsciinwriterRunner(
        typing_delay_range=(0.05, 0.05), jitter_factor=0, post_typing_delay=0.1
    )
    mocker.patch("asciinwriter.__main__.time.sleep")
    mock_print = mocker.patch("builtins.print")
    mock_child = mocker.Mock()

    runner.human_type(mock_child, "hi")

    # Should print each character
    mock_print.assert_any_call("h", end="", flush=True)
    mock_print.assert_any_call("i", end="", flush=True)
