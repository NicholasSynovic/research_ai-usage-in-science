#!/usr/bin/env bash

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

DB_PATH="${DB_PATH:-${REPO_ROOT}/aius.sqlite3}"
BACKEND="${BACKEND:-sophia}"
MODEL_NAME="${MODEL_NAME:-openai/gpt-oss-120b}"
STRIDE="${STRIDE:-20}"
JOBS="${JOBS:-20}"
JOBLOG="${JOBLOG:-${SCRIPT_DIR}/dijkstra.joblog.tsv}"
RESULTS_DIR="${RESULTS_DIR:-${SCRIPT_DIR}/dijkstra.results}"

mkdir -p "${RESULTS_DIR}"

seq 0 19 | parallel \
  --jobs "${JOBS}" \
  --joblog "${JOBLOG}" \
  --results "${RESULTS_DIR}" \
  --line-buffer \
  --tagstring '{#}/20 index={}' \
  aius analyze \
    --db "${DB_PATH}" \
    --backend "${BACKEND}" \
    --model-name "${MODEL_NAME}" \
    --index {} \
    --stride "${STRIDE}"
