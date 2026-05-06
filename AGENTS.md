# AIUS Agent Notes

## Source Of Truth

- Trust `pyproject.toml`, `Makefile`, `.pre-commit-config.yaml`, `ruff.toml`, and `.github/workflows/*` over `README.md`.
- Project package is `aius`; the CLI entrypoint is `aius` -> `aius.main:main`.
- Python target is `~=3.13`; use Python 3.13 locally even though the build workflow still says 3.10.

## Commands

```bash
make create-dev   # pre-commit install + pre-commit autoupdate + rm -rf env + uv sync
make build        # rm -rf dist + uv version <latest git tag> + uv build + uv pip install dist/*.tar.gz
uv sync
uv build
ruff format aius/
ruff check aius/
pytest
```

- `ruff format` is the formatter; `ruff.toml` is authoritative for linting and line length.
- For focused tests, look for `test_*.py` and run the specific file directly; there is no active top-level `tests/` package.

## Repo Shape

- `aius/` is the package code.
- `scripts/`, `figures/`, and `statistics/` are analysis utilities.
- `scripts/_old/` and `figures/_old/` are archival.

## Runtime Flow

- `aius/main.py` builds logging, parses CLI args, then dispatches through `runner_factory`.
- CLI subcommands: `init`, `search`, `openalex`, `jats`, `pandoc`, `analyze`.
- `runner_factory` expects a matching `--db` option for each subcommand.
- `openalex` requires `--email`; `analyze` requires `--backend` and `--model-name`.
- Database access is centralized in `aius.db.DB`; its constructor creates tables and the `natural_science_article_dois` view.

## Conventions

- Keep imports grouped as standard library / third-party / local.
- Use 4-space indentation, double quotes, type hints, and `Path` for filesystem paths when practical.
- Preserve the existing file header style when adding Python files.
- Do not commit secrets or API keys; prefer environment variables or CLI args.

## Gotchas

- `make create-dev` removes the local `env/` directory.
- `pandas.read_sql_table` can mis-handle SQLite timestamp columns here; use a raw SQL query when that happens.
