# (C) 2025 Alexei Znamensky
# Licensed under the GPL-3.0-or-later license. See LICENSES/GPL-3.0-or-later.txt for details.
# SPDX-FileCopyrightText: 2025 Alexei Znamensky
# SPDX-License-Identifier: GPL-3.0-or-later
import os
import tempfile

import pytest

from screenwriter.__main__ import main


def test_main_with_version_argument(mocker):
    """Test that --version argument works."""
    mocker.patch("sys.argv", ["screenwriter", "--version"])
    with pytest.raises(SystemExit) as exc_info:
        main()
    assert exc_info.value.code == 0


def test_main_with_help_argument(mocker):
    """Test that --help argument works."""
    mocker.patch("sys.argv", ["screenwriter", "--help"])
    with pytest.raises(SystemExit) as exc_info:
        main()
    assert exc_info.value.code == 0


def test_main_without_input_file_fails(mocker):
    """Test that main fails when no input file is provided."""
    mocker.patch("sys.argv", ["screenwriter"])
    mocker.patch.dict(os.environ, {}, clear=True)
    with pytest.raises(SystemExit) as exc_info:
        main()
    assert exc_info.value.code == 2  # argparse error code


def test_main_with_env_var_input_file(mocker):
    """Test that main uses PEXP_FILE environment variable."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".pexp", delete=False) as f:
        f.write("SEND(echo hello)\nEXPECT(hello)\n")
        temp_file = f.name

    try:
        mocker.patch("sys.argv", ["screenwriter"])
        mocker.patch.dict(os.environ, {"PEXP_FILE": temp_file})
        mock_spawn = mocker.patch("screenwriter.__main__.pexpect.spawn")
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
    finally:
        os.unlink(temp_file)


def test_main_with_positional_argument(mocker):
    """Test that main uses positional argument for input file."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".pexp", delete=False) as f:
        f.write("SEND(echo hello)\nEXPECT(hello)\n")
        temp_file = f.name

    try:
        mocker.patch("sys.argv", ["screenwriter", temp_file])
        mock_spawn = mocker.patch("screenwriter.__main__.pexpect.spawn")
        mock_child = mocker.Mock()
        mock_spawn.return_value = mock_child
        mock_child.expect.return_value = None

        main()

        # Verify pexpect.spawn was called
        mock_spawn.assert_called_once()
    finally:
        os.unlink(temp_file)


def test_main_positional_arg_overrides_env_var(mocker):
    """Test that positional argument takes precedence over environment variable."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".pexp", delete=False) as f1:
        f1.write("SEND(echo from_arg)\nEXPECT(from_arg)\n")
        arg_file = f1.name

    with tempfile.NamedTemporaryFile(mode="w", suffix=".pexp", delete=False) as f2:
        f2.write("SEND(echo from_env)\nEXPECT(from_env)\n")
        env_file = f2.name

    try:
        mocker.patch("sys.argv", ["screenwriter", arg_file])
        mocker.patch.dict(os.environ, {"PEXP_FILE": env_file})
        mock_spawn = mocker.patch("screenwriter.__main__.pexpect.spawn")
        mock_human_type = mocker.patch("screenwriter.__main__.human_type")
        mock_child = mocker.Mock()
        mock_spawn.return_value = mock_child
        mock_child.expect.return_value = None

        main()

        # Should have called human_type with command from arg_file
        mock_human_type.assert_called_with(mock_child, "echo from_arg\r")
    finally:
        os.unlink(arg_file)
        os.unlink(env_file)


def test_main_file_not_found(mocker):
    """Test that main handles file not found error."""
    mocker.patch("sys.argv", ["screenwriter", "nonexistent.pexp"])
    with pytest.raises(SystemExit) as exc_info:
        main()
    assert exc_info.value.code == 1


def test_main_empty_file_exits_cleanly(mocker):
    """Test that main exits cleanly with empty file."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".pexp", delete=False) as f:
        f.write("")  # Empty file
        temp_file = f.name

    try:
        mocker.patch("sys.argv", ["screenwriter", temp_file])
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 0
    finally:
        os.unlink(temp_file)


def test_main_comments_only_file_exits_cleanly(mocker):
    """Test that main exits cleanly with file containing only comments."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".pexp", delete=False) as f:
        f.write("# This is a comment\n# Another comment\n")
        temp_file = f.name

    try:
        mocker.patch("sys.argv", ["screenwriter", temp_file])
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 0
    finally:
        os.unlink(temp_file)


def test_main_processes_send_and_expect(mocker):
    """Test that main correctly processes SEND and EXPECT commands."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".pexp", delete=False) as f:
        f.write("SEND(echo hello)\nEXPECT(hello world)\nSEND(ls)\n")
        temp_file = f.name

    try:
        mock_spawn = mocker.patch("screenwriter.__main__.pexpect.spawn")
        mock_human_type = mocker.patch("screenwriter.__main__.human_type")
        mock_child = mocker.Mock()
        mock_spawn.return_value = mock_child
        mock_child.expect.return_value = None

        mocker.patch("sys.argv", ["screenwriter", temp_file])
        main()

        # Verify interactions
        mock_spawn.assert_called_once_with(
            "bash",
            encoding="utf-8",
            timeout=600,
        )

        # Should have called human_type twice for SEND commands
        assert mock_human_type.call_count == 2
        mock_human_type.assert_any_call(mock_child, "echo hello\r")
        mock_human_type.assert_any_call(mock_child, "ls\r")

        # Should have called expect twice: once for prompt setup, once for EXPECT command
        assert mock_child.expect.call_count == 2
        mock_child.expect.assert_any_call(r"\$ ")  # Initial prompt setup
        mock_child.expect.assert_any_call("hello\\ world")  # EXPECT command (escaped)

        # Should have called sendeof at the end
        mock_child.sendeof.assert_called_once()

    finally:
        os.unlink(temp_file)


def test_main_filters_comments_and_empty_lines(mocker):
    """Test that main filters out comments and empty lines."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".pexp", delete=False) as f:
        f.write(
            """
# This is a comment
SEND(echo test)

# Another comment
EXPECT(test)

"""
        )
        temp_file = f.name

    try:
        mock_spawn = mocker.patch("screenwriter.__main__.pexpect.spawn")
        mock_human_type = mocker.patch("screenwriter.__main__.human_type")
        mock_child = mocker.Mock()
        mock_spawn.return_value = mock_child
        mock_child.expect.return_value = None

        mocker.patch("sys.argv", ["screenwriter", temp_file])
        main()

        # Should only process the SEND and EXPECT commands, not comments
        mock_human_type.assert_called_once_with(mock_child, "echo test\r")

        # Should have called expect twice: once for prompt setup, once for EXPECT command
        assert mock_child.expect.call_count == 2
        mock_child.expect.assert_any_call(r"\$ ")  # Initial prompt setup
        mock_child.expect.assert_any_call("test")  # EXPECT command

    finally:
        os.unlink(temp_file)
