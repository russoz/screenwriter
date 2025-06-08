#!/usr/bin/env python3
# (C) 2025 Alexei Znamensky
# Licensed under the GPL-3.0-or-later license. See LICENSES/GPL-3.0-or-later.txt for details.
# SPDX-FileCopyrightText: 2025 Alexei Znamensky
# SPDX-License-Identifier: GPL-3.0-or-later
#
import argparse
import os
import random
import re
import sys
import time

import pexpect

from . import __version__


class ScreenwriterRunner:
    """Handles automation of terminal sessions with configurable parameters."""

    VALID_COMMANDS = ["SEND", "EXPECT", "ENTER", "DELAY"]

    command_re = re.compile(
        rf'^\s*(?P<cmd>{"|".join(VALID_COMMANDS)})\((?P<param>.*)\)\s*(?:#.*)?$'
    )

    def __init__(
        self,
        typing_delay_range=(0.03, 0.12),
        jitter_factor=0.01,
        jitter_range=6,
        post_typing_delay=0.2,
        shell="bash",
        shell_prompt=r"\$ ",
        timeout=600,
    ):
        self.typing_delay_range = typing_delay_range
        self.jitter_factor = jitter_factor
        self.jitter_range = jitter_range
        self.post_typing_delay = post_typing_delay
        self.shell = shell
        self.shell_prompt = shell_prompt
        self.timeout = timeout

    def typing_delay(self):
        """Calculate a randomized typing delay with jitter."""
        base_delay = random.uniform(*self.typing_delay_range)
        jitter = self.jitter_factor * random.randint(0, self.jitter_range)
        return base_delay + jitter

    def human_type(self, child, text):
        """Type text with human-like delays."""
        for c in text:
            time.sleep(self.typing_delay())
            child.send(c)
            c = re.sub(r"([^\r])\n", r"\1\r\n", c)  # Convert \n to \r\n
            print(c, end="", flush=True)
        time.sleep(self.typing_delay() + self.post_typing_delay)

    def process_line(self, child, line):
        """Process a single script line."""
        match = self.command_re.match(line)
        if not match:
            print(f"Error: Invalid command format: '{line}'", file=sys.stderr)
            sys.exit(1)

        cmd, param = match.group("cmd"), match.group("param").strip()

        match cmd:
            case "SEND":
                self.human_type(child, param)
            case "EXPECT":
                child.expect(re.escape(param))
            case "ENTER":
                try:
                    count = int(param) if param else 1
                    for _ in range(count):
                        child.send("\r")
                        print("\r", end="", flush=True)
                except ValueError:
                    print(
                        f"Error: ENTER() requires an integer parameter, got '{param}'",
                        file=sys.stderr,
                    )
                    sys.exit(1)
            case "DELAY":
                try:
                    delay = float(param)
                    time.sleep(delay)
                except ValueError:
                    print(
                        f"Error: DELAY() requires a numeric parameter, got '{param}'",
                        file=sys.stderr,
                    )
                    sys.exit(1)

    def process_file(self, input_file):
        """Process the script file line by line."""
        try:
            with open(input_file) as f:
                # Initialize pexpect session
                child = pexpect.spawn(
                    self.shell,
                    encoding="utf-8",
                    timeout=self.timeout,
                )
                child.logfile_read = sys.stdout
                child.setecho(False)
                child.expect(self.shell_prompt)

                try:
                    # Read and process one line at a time
                    for line in f:
                        line = line.strip()
                        if not line or line.startswith("#"):
                            continue

                        self.process_line(child, line)
                finally:
                    child.sendeof()

        except FileNotFoundError:
            print(f"Error: File '{input_file}' not found.", file=sys.stderr)
            sys.exit(1)
        except IOError as e:
            print(f"Error reading file '{input_file}': {e}", file=sys.stderr)
            sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Script and automate interactive terminal sessions for generating asciinema .cast files",
        prog="screenwriter",
    )
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {__version__}"
    )
    parser.add_argument(
        "input_file",
        nargs="?",
        help="Path to the .scene script file (can also be set via SCENE_FILE environment variable)",
    )

    args = parser.parse_args()

    # Determine input file: command line argument takes precedence over environment variable
    input_file = args.input_file or os.environ.get("SCENE_FILE")
    if not input_file:
        parser.error(
            "Input file must be specified either as an argument or via SCENE_FILE environment variable"
        )

    # Create runner with default configuration
    runner = ScreenwriterRunner()
    runner.process_file(input_file)


if __name__ == "__main__":
    main()
