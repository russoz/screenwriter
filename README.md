# Screenwriter

Screenwriter is a CLI tool for scripting and automating interactive terminal sessions, primarily designed to generate [asciinema](https://asciinema.org/) `.cast` files for demos, documentation, and automated testing. It simulates human-like typing and command execution, making it ideal for producing realistic terminal recordings and GIFs.

## Purpose

- Automate terminal interactions for reproducible demos and documentation
- Generate `.cast` files for use with asciinema and conversion to GIFs
- Script complex shell sessions with SEND/EXPECT primitives
- Useful for CI, documentation, and teaching

## Quick Start

Install dependencies (requires Python 3.11+):

```sh
poetry install
```

Prepare a script file (e.g., `demo.pexp`):

```
SEND(echo Hello, world!)
EXPECT(Hello, world!)
```

Run the script and record a cast:

```sh
export PEXP_FILE=demo.pexp
asciinema rec demo.cast -c "poetry run screenwriter"
```

You can then convert the `.cast` to a GIF using [agg](https://github.com/asciinema/agg) or similar tools.

## Usage

Screenwriter reads commands from a file specified by the `PEXP_FILE` environment variable. The file should contain lines like:

- `SEND(...)` sends a command to the shell.
- `EXPECT(...)` waits for the given output.

## Development

- Source code: [`src/screenwriter`](src/screenwriter)
- Tests: [`tests/`](tests/)
- Build: `poetry build`
- Lint: `poetry run flake8 src/screenwriter`

## License

MIT License. See `LICENSES/MIT.txt` for details.

## Author

(C) 2025 Alexei Znamensky
