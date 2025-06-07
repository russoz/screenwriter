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


HUMAN_DELAY = (0.03, 0.12)  # min/max seconds between keystrokes


def typing_delay():
    return random.uniform(*HUMAN_DELAY) + 0.01 * random.randint(0, 6)  # add some jitter


def human_type(child, text):
    for c in text:
        time.sleep(typing_delay())
        child.send(c)
        c = re.sub(r"([^\r])\n", r"\1\r\n", c)  # Convert \n to \r\n
        print(c, end="", flush=True)
    time.sleep(typing_delay() + 0.2)


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
        help="Path to the .pexp script file (can also be set via PEXP_FILE environment variable)",
    )

    args = parser.parse_args()

    # Determine input file: command line argument takes precedence over environment variable
    input_file = args.input_file or os.environ.get("PEXP_FILE")
    if not input_file:
        parser.error(
            "Input file must be specified either as an argument or via PEXP_FILE environment variable"
        )

    try:
        with open(input_file) as f:
            lines = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"Error: File '{input_file}' not found.", file=sys.stderr)
        sys.exit(1)
    except IOError as e:
        print(f"Error reading file '{input_file}': {e}", file=sys.stderr)
        sys.exit(1)

    lines = [line for line in lines if not line.startswith("#")]
    if not lines:
        print("No commands to execute.", file=sys.stderr)
        sys.exit(0)

    child = pexpect.spawn(
        "bash",
        encoding="utf-8",
        timeout=600,
    )
    child.logfile_read = sys.stdout
    child.setecho(False)
    child.expect(r"\$ ")

    for line in lines:
        if line.startswith("SEND(") and line.endswith(")"):
            cmd = line[5:-1]
            human_type(child, f"{cmd}\r")
        elif line.startswith("EXPECT(") and line.endswith(")"):
            pat = line[7:-1]
            # Use regex for matching
            child.expect(re.escape(pat))

    child.sendeof()


if __name__ == "__main__":
    main()
