# (C) 2025 Alexei Znamensky
# Licensed under the GPL-3.0-or-later license. See LICENSES/GPL-3.0-or-later.txt for details.
# SPDX-FileCopyrightText: 2025 Alexei Znamensky
# SPDX-License-Identifier: GPL-3.0-or-later
import os

import pytest

from asciinwriter.__main__ import AsciinwriterRunner
from asciinwriter.__main__ import main


def test_main_with_version_argument(mocker):
    """Test that --version argument works."""
    mocker.patch("sys.argv", ["asciinwriter", "--version"])
    with pytest.raises(SystemExit) as exc_info:
        main()
    assert exc_info.value.code == 0


def test_main_with_help_argument(mocker):
    """Test that --help argument works."""
    mocker.patch("sys.argv", ["asciinwriter", "--help"])
    with pytest.raises(SystemExit) as exc_info:
        main()
    assert exc_info.value.code == 0


def test_main_without_input_file_fails(mocker):
    """Test that main fails when no input file is provided."""
    mocker.patch("sys.argv", ["asciinwriter"])
    mocker.patch.dict(os.environ, {}, clear=True)
    with pytest.raises(SystemExit) as exc_info:
        main()
    assert exc_info.value.code == 2  # argparse error code


def test_main_with_env_var_input_file(mocker, tmp_path):
    """Test that main uses SCENE_FILE environment variable."""
    test_file = tmp_path / "test.scene"
    test_file.write_text("SEND(echo hello)\nEXPECT(hello)\n")

    mocker.patch("sys.argv", ["asciinwriter"])
    mocker.patch.dict(os.environ, {"SCENE_FILE": str(test_file)})
    mock_spawn = mocker.patch("asciinwriter.__main__.pexpect.spawn")
    mock_child = mocker.Mock()
    mock_spawn.return_value = mock_child
    mock_child.expect.return_value = None

    main()

    # Verify pexpect.spawn was called
    mock_spawn.assert_called_once_with(
        "bash",
        encoding="utf-8",
        timeout=600,
    )


def test_main_with_positional_argument(mocker, tmp_path):
    """Test that main uses positional argument for input file."""
    test_file = tmp_path / "test.scene"
    test_file.write_text("SEND(echo hello)\nEXPECT(hello)\n")

    mocker.patch("sys.argv", ["asciinwriter", str(test_file)])
    mock_spawn = mocker.patch("asciinwriter.__main__.pexpect.spawn")
    mock_child = mocker.Mock()
    mock_spawn.return_value = mock_child
    mock_child.expect.return_value = None

    main()

    # Verify pexpect.spawn was called
    mock_spawn.assert_called_once()


def test_main_positional_arg_overrides_env_var(mocker, tmp_path):
    """Test that positional argument takes precedence over environment variable."""
    arg_file = tmp_path / "arg_file.scene"
    arg_file.write_text("SEND(echo from_arg)\nEXPECT(from_arg)\n")

    env_file = tmp_path / "env_file.scene"
    env_file.write_text("SEND(echo from_env)\nEXPECT(from_env)\n")

    mocker.patch("sys.argv", ["asciinwriter", str(arg_file)])
    mocker.patch.dict(os.environ, {"SCENE_FILE": str(env_file)})
    mock_spawn = mocker.patch("asciinwriter.__main__.pexpect.spawn")
    mock_human_type = mocker.patch(
        "asciinwriter.__main__.AsciinwriterRunner.human_type"
    )
    mock_child = mocker.Mock()
    mock_spawn.return_value = mock_child
    mock_child.expect.return_value = None

    main()

    # Should have called human_type with command from arg_file
    mock_human_type.assert_called_with(mock_child, "echo from_arg")


def test_main_file_not_found(mocker):
    """Test that main handles file not found error."""
    mocker.patch("sys.argv", ["asciinwriter", "nonexistent.scene"])
    with pytest.raises(SystemExit) as exc_info:
        main()
    assert exc_info.value.code == 1


def test_main_empty_file_exits_cleanly(mocker, tmp_path):
    """Test that main exits cleanly with empty file."""
    test_file = tmp_path / "empty.scene"
    test_file.write_text("")  # Empty file

    mocker.patch("sys.argv", ["asciinwriter", str(test_file)])
    # Should complete successfully without raising SystemExit
    main()


def test_main_comments_only_file_exits_cleanly(mocker, tmp_path):
    """Test that main exits cleanly with file containing only comments."""
    test_file = tmp_path / "comments.scene"
    test_file.write_text("# This is a comment\n# Another comment\n")

    mocker.patch("sys.argv", ["asciinwriter", str(test_file)])
    # Should complete successfully without raising SystemExit
    main()


def test_main_processes_send_and_expect(mocker, tmp_path):
    """Test that main correctly processes SEND and EXPECT commands."""
    test_file = tmp_path / "commands.scene"
    test_file.write_text("SEND(echo hello)\nEXPECT(hello world)\nSEND(ls)\n")

    mock_spawn = mocker.patch("asciinwriter.__main__.pexpect.spawn")
    mock_human_type = mocker.patch(
        "asciinwriter.__main__.AsciinwriterRunner.human_type"
    )
    mock_child = mocker.Mock()
    mock_spawn.return_value = mock_child
    mock_child.expect.return_value = None

    mocker.patch("sys.argv", ["asciinwriter", str(test_file)])
    main()

    # Verify interactions
    mock_spawn.assert_called_once_with(
        "bash",
        encoding="utf-8",
        timeout=600,
    )

    # Should have called human_type twice for SEND commands
    assert mock_human_type.call_count == 2
    mock_human_type.assert_any_call(mock_child, "echo hello")
    mock_human_type.assert_any_call(mock_child, "ls")

    # Should have called expect twice: once for prompt setup, once for EXPECT command
    assert mock_child.expect.call_count == 2
    mock_child.expect.assert_any_call(r"\$ ")  # Initial prompt setup
    mock_child.expect.assert_any_call("hello\\ world")  # EXPECT command (escaped)

    # Should have called sendeof at the end
    mock_child.sendeof.assert_called_once()


def test_main_filters_comments_and_empty_lines(mocker, tmp_path):
    """Test that main filters out comments and empty lines."""
    test_file = tmp_path / "mixed.scene"
    test_file.write_text(
        """
# This is a comment
SEND(echo test)

# Another comment
EXPECT(test)

"""
    )

    mock_spawn = mocker.patch("asciinwriter.__main__.pexpect.spawn")
    mock_human_type = mocker.patch(
        "asciinwriter.__main__.AsciinwriterRunner.human_type"
    )
    mock_child = mocker.Mock()
    mock_spawn.return_value = mock_child
    mock_child.expect.return_value = None

    mocker.patch("sys.argv", ["asciinwriter", str(test_file)])
    main()

    # Should only process the SEND and EXPECT commands, not comments
    mock_human_type.assert_called_once_with(mock_child, "echo test")

    # Should have called expect twice: once for prompt setup, once for EXPECT command
    assert mock_child.expect.call_count == 2
    mock_child.expect.assert_any_call(r"\$ ")  # Initial prompt setup
    mock_child.expect.assert_any_call("test")  # EXPECT command


def test_main_enter_command(mocker, tmp_path):
    """Test that main correctly processes ENTER command."""
    test_file = tmp_path / "enter.scene"
    test_file.write_text("SEND(echo hello)\nENTER(2)\nSEND(ls)\n")

    mock_spawn = mocker.patch("asciinwriter.__main__.pexpect.spawn")
    mock_child = mocker.Mock()
    mock_spawn.return_value = mock_child
    mock_child.expect.return_value = None

    mocker.patch("sys.argv", ["asciinwriter", str(test_file)])
    main()

    # Should have called send with \r twice for ENTER(2)
    assert mock_child.send.call_count >= 2  # At least 2 calls for ENTER(2)
    # Check for the \r calls specifically
    enter_calls = [
        call for call in mock_child.send.call_args_list if call[0][0] == "\r"
    ]
    assert len(enter_calls) == 2


def test_main_delay_command(mocker, tmp_path):
    """Test that main correctly processes DELAY command."""
    test_file = tmp_path / "delay.scene"
    test_file.write_text("SEND(echo hello)\nDELAY(0.5)\nSEND(ls)\n")

    mock_spawn = mocker.patch("asciinwriter.__main__.pexpect.spawn")
    mock_sleep = mocker.patch("time.sleep")
    mock_child = mocker.Mock()
    mock_spawn.return_value = mock_child
    mock_child.expect.return_value = None

    mocker.patch("sys.argv", ["asciinwriter", str(test_file)])
    main()

    # Should have called time.sleep with 0.5
    mock_sleep.assert_any_call(0.5)


def test_main_enter_invalid_parameter(mocker, tmp_path):
    """Test that main handles invalid ENTER parameter."""
    test_file = tmp_path / "invalid_enter.scene"
    test_file.write_text("ENTER(not_a_number)\n")

    mocker.patch("sys.argv", ["asciinwriter", str(test_file)])
    with pytest.raises(SystemExit) as exc_info:
        main()
    assert exc_info.value.code == 1


def test_main_delay_invalid_parameter(mocker, tmp_path):
    """Test that main handles invalid DELAY parameter."""
    test_file = tmp_path / "invalid_delay.scene"
    test_file.write_text("DELAY(not_a_number)\n")

    mocker.patch("sys.argv", ["asciinwriter", str(test_file)])
    with pytest.raises(SystemExit) as exc_info:
        main()
    assert exc_info.value.code == 1


def test_main_enter_optional_parameter(mocker, tmp_path):
    """Test that main correctly processes ENTER command with optional parameter."""
    test_file = tmp_path / "enter_optional.scene"
    test_file.write_text("SEND(echo hello)\nENTER()\nSEND(ls)\n")

    mock_spawn = mocker.patch("asciinwriter.__main__.pexpect.spawn")
    mock_child = mocker.Mock()
    mock_spawn.return_value = mock_child
    mock_child.expect.return_value = None

    mocker.patch("sys.argv", ["asciinwriter", str(test_file)])
    main()

    # Should have called send with \r once for ENTER() (default 1)
    enter_calls = [
        call for call in mock_child.send.call_args_list if call[0][0] == "\r"
    ]
    assert len(enter_calls) == 1


def test_asciinwriter_runner_enter_optional(mocker):
    """Test that AsciinwriterRunner processes ENTER() with optional parameter correctly."""
    mock_child = mocker.Mock()
    runner = AsciinwriterRunner()

    # Test ENTER() with no parameter (should default to 1)
    runner.process_line(mock_child, "ENTER()")

    # Should have called send with \r once
    enter_calls = [
        call for call in mock_child.send.call_args_list if call[0][0] == "\r"
    ]
    assert len(enter_calls) == 1
