# AIUS Agent Guidelines

Guidance for agentic coding assistants working in this repository. Keep changes
aligned with the research workflow, data integrity, and reproducibility goals.

## Quick Facts

- Package: `aius`
- Python: 3.13 (project requires `~=3.13`)
- Build backend: `hatchling`
- Package manager: `uv`
- CLI entrypoint: `aius` -> `aius.main:main`

## Build, Lint, Test

### Environment setup

```bash
make create-dev   # pre-commit install + uv sync
uv sync           # install deps from lock
```

### Build/install

```bash
make build        # uv build + install sdist
uv build          # build artifacts
```

### Lint/format

```bash
ruff check aius/        # lint (see ruff.toml)
ruff format aius/       # format (ruff formatter)
```

Notes:

- `ruff.toml` defines formatting (double quotes, magic trailing commas) and lint
  rules. Black is configured in `pyproject.toml` with line-length 79 but Ruff
  uses 88 by default; prefer Ruff formatter for consistency.

### Tests

```bash
pytest                         # all tests
pytest tests/test_file.py       # single test file
pytest -k "name_substring"      # subset by name
pytest tests/test_file.py::TestClass::test_name
```

If tests are not under `tests/`, search for `test_*.py` before running.

## Code Style

### Imports

- Group in three blocks: standard library, third-party, local.
- Alphabetize within each block.
- Prefer explicit imports; avoid wildcard imports.

Example:

```python
from datetime import datetime
from pathlib import Path

import pandas as pd

from aius.db import DB
```

### Formatting

- Indent with 4 spaces.
- Use double quotes for strings (Ruff format).
- Line length: 88 for Ruff formatter. Be aware Black is set to 79.
- Use trailing commas in multiline literals/args.
- Use `Path` for file paths when practical.

### Types

- Add type hints for function params and return values.
- Prefer `X | None` over `Optional[X]` in new code.
- Use concrete types in public APIs (e.g., `list[str]`, `dict[str, int]`).
- Keep `Path` and `str` usage consistent at boundaries (convert early).

### Naming

- Classes: `PascalCase`.
- Functions/vars: `snake_case`.
- Constants: `UPPER_SNAKE_CASE`.
- Private members: leading underscore.
- Use descriptive names for domain concepts (e.g., `megajournal_name`).

### Docstrings

- Use concise docstrings for public classes/functions.
- Ruff docstring rules are enabled; keep summaries brief and imperative.
- Longer modules use file headers and module docstrings.

### Error handling

- Prefer explicit exceptions with logging where failures are expected.
- Use `logger.error` for recoverable failures; return status codes when needed.
- Avoid bare `except:`; catch specific exceptions (e.g., `OperationalError`).
- Use `contextlib.suppress` sparingly for tight, well-known cases.

Example:

```python
try:
    db = DB(logger=logger, db_path=db_path)
except OperationalError:
    logger.error("Unable to connect to SQLite3 database: %s", db_path)
    return -1
```

### Logging

- Use the provided `logger` (see `aius.main` setup).
- Prefer structured messages with `%s` placeholders.
- Log data access boundaries (read/write) and major pipeline steps.

## Architecture and Patterns

- Runner pattern: CLI selects a runner via `runner_factory`.
- Each runner returns an `int` status; `0` is success.
- Database access is centralized in `aius.db.DB`.
- Keep CLI arguments in `aius/cli/argparse.py` and map to runner kwargs.

## File/Module Conventions

- `aius/` is the main package.
- `scripts/` and `figures/` contain analysis utilities and plotting scripts.
- Historical scripts live in `scripts/_old` and `figures/_old`.

## Headers

Python files commonly include a header:

```python
# Copyright 2025 (C) Nicholas M. Synovic
```

Follow existing file headers when adding new modules.

## Security and Data Integrity

- Do not commit secrets or API keys.
- Use environment variables or CLI args for credentials.
- Avoid destructive operations on the database; prefer append/update semantics.

## Cursor/Copilot Rules

- No `.cursor/rules/`, `.cursorrules`, or `.github/copilot-instructions.md` were
  found in this repository. If they are added later, mirror their guidance here.
