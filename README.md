# AIUS

AIUS is the codebase behind *An Exploratory Mixed-Methods Study of Deep Neural Network Reuse in Computational Natural Science*. It provides a CLI for building the study database, collecting OpenAlex metadata, downloading JATS XML, converting articles to Markdown, and running LLM-based analysis over the resulting corpus.

## What This Repository Contains

- The `aius` Python package and CLI entrypoint.
- Runners for the study pipeline: `init`, `search`, `openalex`, `jats`, `pandoc`, and `analyze`.
- Analysis, plotting, and historical scripts under `scripts/`, `figures/`, and `statistics/`.
- The code used to reproduce the study workflow; release data is distributed separately through Zenodo.

## Requirements

- Python 3.13
- `uv`
- `make`
- A local `pandoc` service for the `pandoc` step
- An OpenAlex email address for polite-pool access
- An LLM backend for `analyze` (`ollama`, `metis`, or `sophia`)
- The PLOS archive path if you need a non-default JATS source archive

## Install

Create a full development environment:

```bash
make create-dev
```

That installs pre-commit hooks, refreshes hook versions, removes the local `env/` directory if present, and syncs dependencies with `uv`.

To build the package artifacts:

```bash
make build
```

## Run The CLI

The CLI entrypoint is `aius`. By default it uses `aius.sqlite3` in the repository root.

Check the available commands:

```bash
aius --help
aius <subcommand> --help
```

Typical pipeline:

```bash
aius init
aius search --megajournal plos
aius openalex --email you@example.com
aius jats --megajournal plos
aius pandoc
aius analyze --backend ollama --model-name llama3.1 --system-prompt-id uses_dl
```

Notes:

- `init` seeds the SQLite database and creates the tables and views.
- `search` and `jats` accept `--megajournal` values from `bmj`, `f1000`, `frontiersin`, and `plos`.
- `openalex` requires `--email`.
- `analyze` requires `--backend` and `--model-name`; it also accepts `--system-prompt-id` values such as `uses_dl`, `uses_ptms`, `identify_ptms`, `identify_ptm_reuse`, and `identify_ptm_impact`.
- `pandoc` defaults to `http://localhost:3030`.
- `jats` defaults to `allofplos.zip` in the repository root.

## Data And Reproducibility

The study data and supporting artifacts are released separately through Zenodo. The repository keeps the code, while the database and other study outputs are intended to be reused from the archived release.

OpenAlex responses are stored in the SQLite database so later steps can reuse the captured metadata instead of depending on changing upstream results.

## Contributing

Use the development environment above and run the pre-commit hooks locally before sending changes. The repository is configured to format and lint through pre-commit, so that is the best first check.

Please keep changes aligned with the existing CLI runner flow and avoid committing secrets or API keys.
