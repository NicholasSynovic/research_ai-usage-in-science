# AIUS - AI Usage in Science: Agent Guidelines

This file contains development guidelines for agentic coding agents working on
the AIUS (AI Usage in Science) research tool.

## Project Overview

AIUS is a Python research tool for empirically measuring pre-trained deep
learning model (PTM) usage and its impact in natural science publications. It
analyzes scientific papers, extracts AI usage information, and provides
statistical insights.

## Development Environment

**Package Manager:** `uv` (modern Python package manager) **Build System:**
hatchling **Python Version:** 3.13+ (target-version py310 in ruff.toml)

### Environment Setup

```bash
make create-dev    # Setup development environment with pre-commit hooks
uv sync           # Install dependencies from lock file
```

## Build/Lint/Test Commands

### Essential Commands

```bash
# Build and install locally
make build

# Linting and formatting (pre-commit hooks run automatically)
ruff check aius/           # Lint code
ruff format aius/          # Format code
isort aius/                # Sort imports

# Testing
pytest                     # Run all tests
pytest path/to/test.py     # Run specific test file
pytest -k "test_name"      # Run specific test by name

# Security analysis
bandit -r aius/           # Security vulnerability scan
```

### Single Test Commands

```bash
pytest tests/test_specific_file.py::test_function_name
pytest -v tests/test_specific_file.py::test_function_name  # Verbose output
pytest -x tests/  # Stop on first failure
```

## Code Style Guidelines

### Code Formatting

- **Line Length:** 88 characters (ruff), 79 characters (isort/black)
- **Indentation:** 4 spaces
- **Quotes:** Double quotes for strings
- **Trailing Commas:** Enabled for multi-line structures

### Naming Conventions

- **Classes:** PascalCase (e.g., `AnalysisRunner`, `COSTAR_SystemPrompt`)
- **Functions/Variables:** snake_case
- **Constants:** UPPER_SNAKE_CASE (e.g., `DEFAULT_DATABASE_PATH`)
- **Private members:** Prefix with underscore (\_private_method)

### Import Organization

1. Standard library imports (sorted alphabetically)
1. Third-party imports (sorted alphabetically)
1. Local imports (sorted alphabetically)

```python
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from openai import OpenAI

from aius.core.database import DB
from aius.runners.base import Runner
```

### Type Hints

- Use type hints for all function parameters and return values
- Use Union types (e.g., `Runner | int`) instead of Optional when appropriate
- Use `Path` for file paths instead of strings

```python
def connect_to_db(logger: Logger, db_path: Path) -> DB | int:
    """Connect to SQLite3 database."""
```

## Architecture Patterns

### Design Patterns Used

- **Factory Pattern:** For creating runners (`runner_factory`)
- **Template Method:** For common runner workflows
- **ABC Base Classes:** For defining interfaces

### File Organization

- **aius/**: Main package with core functionality
- **scripts/**: Standalone analysis scripts
- **figures/**: Data visualization scripts
- **statistics/**: Statistical analysis modules
- **data/**: Data storage

## Error Handling

### Exception Handling Patterns

```python
try:
    db = DB(logger=logger, db_path=db_path)
    logger.info("Connected to SQLite3 database: %s", db_path)
except OperationalError:
    logger.error("Database connection failed")
    return -1
```

### Logging

- Use the provided logger instance for all logging
- Log at appropriate levels (INFO for normal operations, ERROR for failures)
- Include relevant context in log messages

## Pre-commit Hooks

The following hooks run automatically:

- ruff (linting + formatting)
- isort (import sorting)
- black (code formatting)
- mdformat (markdown formatting)
- bandit (security analysis)
- File validation (JSON, YAML, XML, TOML)
- detect-private-key (security)

## Key Dependencies

### Core Libraries

- **Data Processing:** pandas, numpy, pyarrow, sqlalchemy
- **Scientific Computing:** matplotlib, seaborn, upsetplot
- **AI/LLM Integration:** openai, ollama
- **Web/API:** requests, beautifulsoup4, globus-sdk
- **Document Processing:** pypdf, pandoc
- **CLI Interface:** click, argparse

## Development Workflow

1. Make changes to code
1. Pre-commit hooks will automatically run
1. If hooks fail, fix the issues (most will be auto-fixable by ruff/isort)
1. Run tests to ensure functionality
1. Commit changes

## Testing Strategy

- Limited test coverage currently - focus on critical path testing
- Use pytest for all new tests
- Test file naming: `test_*.py`
- Test function naming: `test_*`

## Security Considerations

- No secrets or keys should be committed to the repository
- Use environment variables for sensitive configuration
- Run bandit security analysis regularly
- Follow OWASP guidelines for data handling

## Code Review Guidelines

When reviewing code, check for:

- Proper type hints and documentation
- Correct import organization
- Appropriate error handling and logging
- Security best practices
- Performance considerations for data processing

## Common Patterns to Follow

### Database Operations

```python
def connect_to_db(logger: Logger, db_path: Path) -> DB | int:
    try:
        db = DB(logger=logger, db_path=db_path)
        logger.info("Connected to SQLite3 database: %s", db_path)
        return db
    except OperationalError:
        logger.error("Database connection failed")
        return -1
```

### Runner Factory Pattern

```python
def runner_factory(logger: Logger, runner_name: str, **kwargs) -> Runner | int:
    match runner_name:
        case "init":
            runner = InitRunner(logger=logger, **kwargs)
        case "download":
            runner = DownloadRunner(logger=logger, **kwargs)
        case _:
            logger.error("Unknown runner: %s", runner_name)
            return -1
    return runner
```

## File Headers

All Python files should include the standard copyright header:

```python
# Copyright 2025 (C) Nicholas M. Synovic
```

## Additional Notes

- This is a scientific research tool - prioritize data integrity and
  reproducibility
- Use Path objects for file operations instead of strings
- Follow modern Python practices (match-case, type unions, etc.)
- Keep functions focused and modular
- Document complex algorithms and data processing steps
