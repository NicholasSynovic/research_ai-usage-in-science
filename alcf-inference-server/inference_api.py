#!/usr/bin/env python3
"""
ALCF Sophia completions client CLI
- argparse CLI for api_key, prompt_id, input markdown, output json
- requests wrapper with exponential backoff (5 retries) and 60s timeout
- submit a chat-style POST to ALCF Sophia completions endpoint
- write response status and JSON to output file
- logging to timestamped file
"""

from __future__ import annotations

import argparse
import json
import logging
import math
import os
import sys
import time
from datetime import datetime
from typing import Any, Dict, Optional

import requests

# ---------------------------
# Config / prompt templates
# ---------------------------

PROMPT_TEMPLATES: Dict[str, str] = {
    "uses-dl": (
        "System: You are an assistant that inspects scientific prose and answers whether the "
        "manuscript describes the use of pre-trained deep learning models (yes/no) and provide "
        "a brief justification. Respond as JSON with keys: result (bool), prose (string)."
    ),
    "uses-ptms": (
        "System: You are an assistant that inspects scientific prose and answers whether the "
        "manuscript describes use of pre-trained PTMs (protein/translational models) (yes/no) with "
        "a brief justification. Respond as JSON with keys: result (bool), prose (string)."
    ),
    "identify-ptms": (
        "System: Identify any pre-trained models mentioned in this document. Return a JSON array "
        "where each item is an object with keys model (string) and prose (string). If none found, "
        "return an empty array."
    ),
    "identify-ptm-reuse-patterns": (
        "System: Analyze the provided scientific prose and identify reuse patterns of pre-trained "
        "models (e.g., fine-tuning, feature extraction, transfer). Return JSON array of objects "
        "with fields model (string), form (string), classification (string), prose (string)."
    ),
    "identify-scientific-process": (
        "System: Extract and identify scientific processes described (e.g., training, cross-validation, "
        "pruning). Return a JSON array of objects with keys: process (string), description (string)."
    ),
}

# Default base url for Sophia (vLLM). The completions endpoint path below appended.
DEFAULT_BASE_URL = "https://inference-api.alcf.anl.gov/resource_server/sophia/vllm/v1"
COMPLETIONS_PATH = "/completions"  # POST to {base_url}/completions


# ---------------------------
# Requests client with retries
# ---------------------------


class RequestsClient:
    """
    Simple requests wrapper that performs GET/POST with exponential backoff retries.
    - retries: number of attempts (default 5)
    - timeout: per-request timeout in seconds (default 60)
    - backoff_factor: base backoff multiplier (sleep = backoff_factor * 2**(attempt-1))
    """

    def __init__(
        self,
        timeout: int = 60,
        retries: int = 5,
        backoff_factor: float = 1.0,
        session: Optional[requests.Session] = None,
    ) -> None:
        self.timeout = timeout
        self.retries = retries
        self.backoff_factor = backoff_factor
        self.session = session or requests.Session()

    def _request_with_backoff(
        self, method: str, url: str, **kwargs
    ) -> requests.Response:
        last_exc: Optional[Exception] = None
        for attempt in range(1, self.retries + 1):
            try:
                logging.info(
                    "Request attempt %d -> %s %s", attempt, method.upper(), url
                )
                resp = self.session.request(
                    method=method, url=url, timeout=self.timeout, **kwargs
                )
                logging.info(
                    "Response status: %s for %s %s",
                    resp.status_code,
                    method.upper(),
                    url,
                )
                return resp
            except (requests.Timeout, requests.ConnectionError) as exc:
                last_exc = exc
                # compute sleep with exponential backoff
                sleep_seconds = self.backoff_factor * (2 ** (attempt - 1))
                # cap at 60 seconds per sleep to be friendly
                sleep_seconds = min(sleep_seconds, 60)
                logging.warning(
                    "Request attempt %d failed (%s). Sleeping %.1f seconds before retry...",
                    attempt,
                    str(exc),
                    sleep_seconds,
                )
                time.sleep(sleep_seconds)
        # If we exit loop, raise the last exception
        logging.error(
            "All %d attempts failed for %s %s", self.retries, method.upper(), url
        )
        if last_exc:
            raise last_exc
        raise RuntimeError("Unexpected error in request retry logic")

    def get(self, url: str, **kwargs) -> requests.Response:
        return self._request_with_backoff("get", url, **kwargs)

    def post(self, url: str, **kwargs) -> requests.Response:
        return self._request_with_backoff("post", url, **kwargs)


# ---------------------------
# Utilities
# ---------------------------


def mask_key(key: str, show_last: int = 4) -> str:
    if not key:
        return "<empty>"
    if len(key) <= show_last:
        return "*" * len(key)
    return "*" * (len(key) - show_last) + key[-show_last:]


def write_output_file(path: str, status_code: int, payload: Any) -> None:
    out = {"status_code": status_code, "response": payload}
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2, ensure_ascii=False)


# ---------------------------
# Main submit logic
# ---------------------------


def build_payload_for_prompt(
    prompt_id: str, system_prompt: str, markdown_text: str, model: str
) -> Dict[str, Any]:
    """
    Build a chat-completions-style payload. Sophia's vLLM endpoint supports OpenAI-like chat format.
    We include the system prompt and the markdown document as the user message.
    """
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": markdown_text},
    ]

    payload = {
        "model": model,
        "messages": messages,
    }
    return payload


def submit_to_sophia(
    client: RequestsClient,
    base_url: str,
    api_key: str,
    model: str,
    system_prompt: str,
    markdown_text: str,
    output_json: str,
) -> int:
    url = base_url.rstrip("/") + COMPLETIONS_PATH
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    payload = build_payload_for_prompt(
        prompt_id="",
        system_prompt=system_prompt,
        markdown_text=markdown_text,
        model=model,
    )
    logging.debug("Payload built: keys=%s", list(payload.keys()))

    try:
        resp = client.post(url, headers=headers, json=payload)
    except Exception as exc:
        logging.exception("Request failed after retries: %s", exc)
        # write failure to output file
        write_output_file(output_json, status_code=0, payload={"error": str(exc)})
        return 1

    # Try to parse JSON, otherwise capture text
    try:
        resp_json = resp.json()
    except ValueError:
        resp_json = {"text": resp.text}

    # Write to output file
    write_output_file(output_json, status_code=resp.status_code, payload=resp_json)
    logging.info("Wrote response to %s (status %d)", output_json, resp.status_code)

    if not resp.ok:
        logging.error("Non-OK response from server: %s", resp.status_code)
        return 2

    return 0


# ---------------------------
# CLI / main
# ---------------------------


def configure_logging(log_dir: str = ".", level: int = logging.INFO) -> str:
    ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    log_filename = os.path.join(log_dir, f"alcf_submit_{ts}.log")
    # basic file handler + console
    logger = logging.getLogger()
    logger.setLevel(level)

    # Avoid adding multiple handlers in interactive re-runs
    if not logger.handlers:
        fh = logging.FileHandler(log_filename, encoding="utf-8")
        fh.setLevel(level)
        fmt = logging.Formatter("%(asctime)s %(levelname)s %(name)s - %(message)s")
        fh.setFormatter(fmt)
        logger.addHandler(fh)

        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(logging.INFO)
        ch.setFormatter(logging.Formatter("%(levelname)s - %(message)s"))
        logger.addHandler(ch)

    logging.info("Logging to %s", log_filename)
    return log_filename


def read_markdown_file(path: str) -> str:
    with open(path, "r", encoding="utf-8") as fh:
        return fh.read()


def parse_args(argv: Optional[list[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Submit a scientific markdown document to ALCF Sophia completions API"
    )
    parser.add_argument(
        "--api-key", required=True, help="ALCF inference server API key (Bearer token)"
    )
    parser.add_argument(
        "--prompt-id",
        required=True,
        choices=list(PROMPT_TEMPLATES.keys()),
        help="Which prompt template to use",
    )
    parser.add_argument(
        "--input-md", required=True, help="Path to Markdown file with scientific prose"
    )
    parser.add_argument(
        "--output-json", required=True, help="Path to write response JSON (and status)"
    )
    parser.add_argument(
        "--model", default="Meta-Llama-3.1-8B-Instruct", help="Model name to request"
    )
    parser.add_argument(
        "--base-url",
        default=DEFAULT_BASE_URL,
        help="Base URL for Sophia vLLM endpoints",
    )
    parser.add_argument(
        "--log-dir", default=".", help="Directory to write timestamped logs"
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=60,
        help="Per-request timeout seconds (default 60)",
    )

    return parser.parse_args(argv)


def main(argv: Optional[list[str]] = None) -> int:
    args = parse_args(argv)
    logpath = configure_logging(log_dir=args.log_dir)

    # Mask API key in logs
    logging.info(
        "Using model=%s, prompt_id=%s, input=%s, output=%s",
        args.model,
        args.prompt_id,
        args.input_md,
        args.output_json,
    )
    logging.debug("API key (masked): %s", mask_key(args.api_key))

    # Validate input markdown file
    if not os.path.isfile(args.input_md):
        logging.error("Input markdown file not found: %s", args.input_md)
        return 2

    markdown_text = read_markdown_file(args.input_md)

    system_prompt = PROMPT_TEMPLATES.get(args.prompt_id)
    if system_prompt is None:
        logging.error("Unknown prompt id: %s", args.prompt_id)
        return 2

    # create requests client
    client = RequestsClient(timeout=args.timeout, retries=5, backoff_factor=1.0)

    logging.info("Submitting to Sophia at %s", args.base_url)
    rc = submit_to_sophia(
        client=client,
        base_url=args.base_url,
        api_key=args.api_key,
        model=args.model,
        system_prompt=system_prompt,
        markdown_text=markdown_text,
        output_json=args.output_json,
    )

    logging.info("Finished with return code %d", rc)
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
