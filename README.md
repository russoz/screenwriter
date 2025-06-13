# Asciinwriter

Asciinwriter is a CLI tool for scripting and automating interactive terminal sessions, primarily designed to generate [asciinema](https://asciinema.org/) `.cast` files for demos, documentation, and automated testing. It simulates human-like typing and command execution, making it ideal for producing realistic terminal recordings and GIFs.

## Purpose

- Automate terminal interactions for reproducible demos and documentation
- Generate `.cast` files for use with asciinema and conversion to GIFs
- Script complex shell sessions with SEND/EXPECT primitives
- Useful for CI, documentation, and teaching

## Quick Start

Install dependencies (requires Python 3.11+):

```sh
pipx install asciinwriter
```

Prepare a script file (e.g., `demo.scene`):

```
SEND(echo Hello, world!)
ENTER()
EXPECT(Hello, world!)
```

Run the script and record a cast:

```sh
export SCENE_FILE=demo.scene
asciinema rec demo.cast -c asciinwriter
```

You can then convert the `.cast` to a GIF using [agg](https://github.com/asciinema/agg) or similar tools.

## Usage

Asciinwriter reads commands from a scene file specified by the `SCENE_FILE` environment variable. The file should contain lines like:

- `SEND(...)` sends text to the shell.
- `ENTER()` sends the Enter key to the shell.
- `EXPECT(...)` waits for the given output.
- `DELAY(...)` pause the typing for a specified period.

## Development

- Source code: [`src/asciinwriter`](src/asciinwriter)
- Tests: [`tests/`](tests/)
- Build: `poetry build`
- Lint: `poetry run flake8 src/asciinwriter`

## License

GPL-3.0-or-later License. See `LICENSES/GPL-3.0-or-later.txt` for details.

## Author

(C) 2025 Alexei Znamensky
