# AIUS Agent Notes

## Source Of Truth

- Trust `pyproject.toml`, `Makefile`, `.pre-commit-config.yaml`, `ruff.toml`, and `.github/workflows/*` over `README.md`.
- The package is `aius`; the CLI entrypoint is `aius` -> `aius.main:main`.
- The repo targets Python 3.13 locally (`requires-python = "~=3.13"` and pre-commit uses `python3.13`), even though the GitHub workflows still say 3.10.

## Commands

```bash
make create-dev   # installs hooks, refreshes hook versions, removes env/, runs uv sync
make build        # removes dist/, bumps version from latest git tag, builds, installs the tarball
uv sync
uv build
ruff format aius/
ruff check aius/
pytest
```

- `make create-dev` deletes the local `env/` directory.
- `ruff format` is the formatter; `ruff.toml` is the lint/format source of truth.
- For focused tests, run the specific `test_*.py` file directly when one exists; this repo does not have an active top-level `tests/` package.

## Repo Shape

- `aius/` contains the application code and CLI flow.
- `scripts/`, `figures/`, and `statistics/` are analysis/reproduction utilities.
- `scripts/_old/` and `figures/_old/` are archival.

## Runtime Flow

- `aius/main.py` sets up logging, parses CLI args, then dispatches through `runner_factory`.
- CLI subcommands are `init`, `search`, `openalex`, `jats`, `pandoc`, and `analyze`.
- Each subcommand expects its own `--db` option; `openalex` also requires `--email`, and `analyze` requires `--backend` and `--model-name`.
- `aius.db.DB` creates the SQLite tables and the `natural_science_article_dois` view on init.

## Gotchas

- The GitHub build workflow is stale: it still references Python 3.10 and calls `make package`, but the Makefile only defines `build` and `create-dev`.
- `pandas.read_sql_table` can mis-handle SQLite timestamp columns here; use a raw SQL query when that happens.
- Do not commit secrets or API keys; use environment variables or CLI args.
