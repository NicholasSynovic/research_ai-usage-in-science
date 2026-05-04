# AIUS Agent Notes

## Source Of Truth

- Trust `pyproject.toml`, `Makefile`, `.pre-commit-config.yaml`, `ruff.toml`, and `.github/workflows/*` over `README.md`; the README still has stale placeholders and commands.
- Project package is `aius`; CLI entrypoint is `aius` -> `aius.main:main`.
- Python requirement is `~=3.13`; use Python 3.13 locally even though the GitHub workflow files still show Python 3.10.

## Common Commands

```bash
make create-dev   # pre-commit install + pre-commit autoupdate + rm -rf env + uv sync
make build        # rm -rf dist + uv version <latest git tag> + uv build + uv pip install dist/*.tar.gz
uv sync
uv build
ruff check aius/
ruff format aius/
pytest
```

- `ruff format` is the formatter to use. `ruff.toml` is authoritative for line length and linting; do not follow the Black 79-char setting in `pyproject.toml`.
- If you need a focused test run, search for `test_*.py` first. There is no active top-level `tests/` package in the current tree.

## Repo Shape

- `aius/` is the package code.
- `scripts/`, `figures/`, and `statistics/` are analysis/plotting utilities.
- `scripts/_old/` and `figures/_old/` are archival.

## Runtime Flow

- `aius/main.py` builds logging, parses CLI args, then dispatches through `runner_factory`.
- The CLI subcommands are `init`, `search`, `openalex`, `jats`, `pandoc`, and `analyze`.
- `runner_factory` expects a matching `--db` option for each subcommand and routes to the corresponding runner class.
- Runners return an `int`; `0` means success.
- `openalex` requires `--email`; `analyze` requires `--backend` and `--model-name`.
- Database access is centralized in `aius.db.DB`.

## Style And Safety

- Keep imports in standard-library / third-party / local groups.
- Use 4-space indentation, double quotes, type hints, and `Path` for filesystem paths when practical.
- Use the existing file header style when adding Python files.
- Do not commit secrets or API keys; prefer environment variables or CLI args.
