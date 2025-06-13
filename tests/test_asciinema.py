# (C) 2025 Alexei Znamensky
# Licensed under the GPL-3.0-or-later license. See LICENSES/GPL-3.0-or-later.txt for details.
# SPDX-FileCopyrightText: 2025 Alexei Znamensky
# SPDX-License-Identifier: GPL-3.0-or-later
import json
import os
import subprocess

import pytest


@pytest.fixture
def asciinema_preexec(pytestconfig):
    """
    Returns os.setsid to silence asciinema output unless verbosity is -vv or higher.
    Fixture to provide the appropriate preexec_fn for asciinema subprocess calls based on pytest verbosity.
    """
    if pytestconfig.option.verbose < 2:  # Default, -q, or -v
        return os.setsid
    return None  # -vv or higher


def test_session(tmp_path, asciinema_preexec):
    """Test that asciinema can record a asciinwriter session and produce a valid .cast file."""
    # Create a simple script file
    script_file = tmp_path / "test_script.scene"
    script_file.write_text(
        "SEND(echo 'Hello from asciinwriter!')\n"
        "ENTER()\n"
        "EXPECT(Hello from asciinwriter!)\n"
        "SEND(date)\n"
        "ENTER()\n"
        "SEND(echo 'Test complete')\n"
        "ENTER()\n"
        "EXPECT(Test complete)\n"
    )

    # Create output file for asciinema
    cast_file = tmp_path / "recording.cast"

    # Run asciinema to record asciinwriter session
    cmd = [
        "asciinema",
        "rec",
        str(cast_file),
        "--command",
        f"asciinwriter {script_file}",
        "--overwrite",
    ]

    result = subprocess.run(
        cmd,
        cwd=str(tmp_path),
        capture_output=True,
        text=True,
        preexec_fn=asciinema_preexec,
    )

    # Check that asciinema completed successfully
    assert result.returncode == 0, f"asciinema failed: {result.stderr}"

    # Check that the cast file was created
    assert cast_file.exists(), "Cast file was not created"
    assert cast_file.stat().st_size > 0, "Cast file is empty"

    # Validate the cast file format
    with open(cast_file) as f:
        lines = f.readlines()

    # First line should be the header (JSON)
    assert len(lines) > 0, "Cast file has no content"

    header = json.loads(lines[0])
    assert "version" in header
    assert "width" in header
    assert "height" in header
    assert "timestamp" in header

    # Subsequent lines should be events
    events_found = 0
    output_events = []

    for line in lines[1:]:
        if line.strip():
            event = json.loads(line)
            assert len(event) == 3, f"Invalid event format: {event}"
            timestamp, event_type, data = event
            assert isinstance(timestamp, (int, float))
            assert event_type in ["i", "o"], f"Invalid event type: {event_type}"
            assert isinstance(data, str)
            events_found += 1

            if event_type == "o":
                output_events.append(data)

    assert events_found > 0, "No events found in cast file"

    # Check that expected output appears in the recording
    full_output = "".join(output_events)
    assert (
        "Hello from asciinwriter!" in full_output
    ), "Expected output not found in recording"


def test_playback(tmp_path, asciinema_preexec):
    """Test that asciinema can play back a recording created with asciinwriter."""
    # Create a simple script
    script_file = tmp_path / "playback_test.scene"
    script_file.write_text(
        "SEND(echo 'Playback test')\n"
        "ENTER()\n"
        "EXPECT(Playback test)\n"
        "SEND(whoami)\n"
        "ENTER()\n"
    )

    cast_file = tmp_path / "playback.cast"

    # Record with asciinema
    record_cmd = [
        "asciinema",
        "rec",
        str(cast_file),
        "--command",
        f"asciinwriter {script_file}",
        "--overwrite",
    ]

    record_result = subprocess.run(
        record_cmd,
        cwd=str(tmp_path),
        capture_output=True,
        text=True,
        preexec_fn=asciinema_preexec,
    )

    assert record_result.returncode == 0, f"Recording failed: {record_result.stderr}"
    assert cast_file.exists()

    # Test playback (just validate command works, don't wait for full playback)
    play_cmd = ["asciinema", "play", str(cast_file), "--speed", "10"]

    # Use Popen to start playback and immediately terminate it
    process = subprocess.Popen(
        play_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )

    # Give it a moment to start, then terminate
    try:
        process.wait(timeout=2)
    except subprocess.TimeoutExpired:
        process.terminate()
        process.wait(timeout=5)

    # The important thing is that asciinema play started without immediate errors
    # A non-zero return code from termination is expected and ok


def test_env_var(tmp_path, asciinema_preexec):
    """Test asciinwriter integration using SCENE_FILE environment variable with asciinema."""
    # Create script file
    script_file = tmp_path / "env_test.scene"
    script_file.write_text(
        "SEND(echo 'Environment variable test')\n"
        "ENTER()\n"
        "EXPECT(Environment variable test)\n"
    )

    cast_file = tmp_path / "env_test.cast"

    # Run asciinema with asciinwriter using environment variable
    cmd = [
        "asciinema",
        "rec",
        str(cast_file),
        "--overwrite",
        "--command",
        "asciinwriter",
    ]

    env = os.environ.copy()
    env["SCENE_FILE"] = str(script_file)

    result = subprocess.run(
        cmd,
        cwd=str(tmp_path),
        env=env,
        capture_output=True,
        text=True,
        preexec_fn=asciinema_preexec,
    )
    assert (
        result.returncode == 0
    ), f"asciinema rec (env var test) failed: {result.stderr}"

    # Check recording was created
    assert cast_file.exists(), "Cast file was not created with environment variable"

    # Validate basic cast file structure
    with open(cast_file) as f:
        content = f.read()

    assert len(content) > 0, "Cast file is empty"
    lines = content.strip().split("\n")
    assert len(lines) >= 1, "Cast file should have at least a header"

    # First line should be valid JSON header
    header = json.loads(lines[0])
    assert "version" in header


def test_complex(tmp_path, asciinema_preexec):
    """Test a more complex asciinwriter session with multiple commands and expects."""
    script_file = tmp_path / "complex_test.scene"
    script_file.write_text(
        "# Complex test script\n"
        "SEND(echo 'Starting complex test')\n"
        "ENTER()\n"
        "EXPECT(Starting complex test)\n"
        "SEND(ls -la /tmp)\n"
        "ENTER()\n"
        "DELAY(0.5)\n"
        "SEND(echo 'Current directory:')\n"
        "ENTER()\n"
        "EXPECT(Current directory:)\n"
        "SEND(pwd)\n"
        "ENTER()\n"
        "SEND(echo 'Test completed successfully')\n"
        "ENTER()\n"
        "EXPECT(Test completed successfully)\n"
    )

    cast_file = tmp_path / "complex.cast"

    # Record the session
    cmd = [
        "asciinema",
        "rec",
        str(cast_file),
        "--overwrite",
        "--title",
        "Complex Asciinwriter Test",
        "--command",
        f"asciinwriter {script_file}",
    ]

    result = subprocess.run(
        cmd,
        cwd=str(tmp_path),
        capture_output=True,
        text=True,
        preexec_fn=asciinema_preexec,
    )

    assert result.returncode == 0, f"Complex test failed: {result.stderr}"
    assert cast_file.exists()

    # Parse and validate the recording
    with open(cast_file) as f:
        lines = f.readlines()

    # Check header
    header = json.loads(lines[0])
    assert header.get("title") == "Complex Asciinwriter Test"

    # Count meaningful events (output events with actual content)
    output_events = []
    for line in lines[1:]:
        if line.strip():
            event = json.loads(line)
            if event[1] == "o" and event[2].strip():  # output event with content
                output_events.append(event[2])

    full_output = "".join(output_events)

    # Verify expected content appears
    assert "Starting complex test" in full_output
    assert "Current directory:" in full_output
    assert "Test completed successfully" in full_output
