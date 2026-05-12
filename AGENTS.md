# AIUS Agent Notes

## Source Of Truth

- Trust `pyproject.toml`, `Makefile`, `.pre-commit-config.yaml`, `ruff.toml`, and `.github/workflows/*` over `README.md`.
- Local development targets Python 3.13 (`requires-python = "~=3.13"`; pre-commit uses `python3.13`).
- The CLI entrypoint is `aius` -> `aius.main:main`.

## Commands

- `make create-dev` installs hooks, refreshes hook versions, deletes local `env/`, and runs `uv sync`.
- `make build` removes `dist/`, bumps the version from the latest git tag, builds, and installs the tarball.
- `ruff format aius/` and `ruff check aius/` are the code-style checks.
- `pytest` is the repo-wide test command.

## Repo Shape

- `aius/main.py` sets up timestamped file logging (`aius_<timestamp>.log` in the repo root), parses CLI args, then dispatches through `runner_factory`.
- CLI subcommands are `init`, `search`, `openalex`, `jats`, `pandoc`, and `analyze`.
- `aius.db.DB` creates the SQLite schema and the `natural_science_article_dois` view during initialization.
- `aius/` is the application package; `scripts/`, `figures/`, and `statistics/` are analysis/reproduction code, with `*_old/` directories archival.

## Workflow Notes

- Each subcommand accepts its own `--db`, defaulting to `aius.sqlite3`.
- `openalex` requires `--email`; `analyze` requires `--backend` and `--model-name`.
- `pandoc` defaults to `http://localhost:3030`; `jats` defaults to `allofplos.zip`.
- The GitHub workflows are stale: they still set up Python 3.10, and `.github/workflows/build.yml` calls `make package`, but the Makefile only defines `build` and `create-dev`.
