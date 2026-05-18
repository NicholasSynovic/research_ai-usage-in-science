# AIUS Agent Notes

## Source Of Truth

- Trust `pyproject.toml`, `Makefile`, `.pre-commit-config.yaml`, and `ruff.toml` over `README.md`.
- The project targets Python 3.13 in `pyproject.toml`; pre-commit uses `python3.13`.
- `ruff.toml` still targets `py310`, so Ruff behavior follows that config, not the project Python floor.
- The CLI entrypoint is `aius` -> `aius.main:main`.

## Commands

- `make create-dev` installs pre-commit, runs `pre-commit autoupdate`, removes local `env/`, and runs `uv sync`.
- `make build` removes `dist/`, rewrites the project version from the latest git tag, builds, and installs the tarball.
- `pytest` is the repo-wide test command.
- Run `ruff format` and `ruff check` on touched Python files.

## Repo Shape

- `aius/main.py` sets up timestamped file logging in the repo root (`aius_<timestamp>.log`), parses CLI args, then dispatches through `runner_factory`.
- CLI subcommands are `init`, `search`, `openalex`, `jats`, `pandoc`, and `analyze`.
- `aius.db.DB` creates the SQLite schema and the `natural_science_article_dois` view during initialization.
- `aius/` is the application package; `figures/`, `scripts/`, and `statistics/` are analysis/reproduction code, with `*_old/` directories archival.

## Workflow Notes

- Each subcommand accepts its own `--db`, defaulting to `aius.sqlite3` in the repo root.
- `openalex` requires `--email`.
- `analyze` requires `--backend` and `--model-name`.
- `pandoc` defaults to `http://localhost:3030`.
- `jats` defaults to `allofplos.zip`.
- Figure scripts in `figures/` are standalone Click CLIs.
