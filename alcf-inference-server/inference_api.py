"""
ALCF Sophia completions client CLI
- argparse CLI for api_key, prompt_id, input markdown, output json
- requests wrapper with exponential backoff (5 retries) and 60s timeout
- submit a chat-style POST to ALCF Sophia completions endpoint
- write response status and JSON to output file
- logging to timestamped file
"""

import argparse
import json
import logging
import os
import sys
from argparse import Namespace
from datetime import datetime, timezone
from json import dump, loads
from logging import Logger
from pathlib import Path
from time import time
from typing import Any, Dict, Optional

from mdformat import text
from openai import OpenAI
from openai.types.chat.chat_completion import ChatCompletion
from pydantic import BaseModel

PROMPT_TEMPLATES: Dict[str, str] = {
    "uses-dl": text(
        md="""
## (C) Context
You are an AI model integrated into an automated pipeline that processes academic computational Natural Science papers into a machine readable format. Your sole responsibility is to evaluate the paper's content and determine whether the author's use deep learning models or methods in their methodology. Your response will be consumed by downstream systems that require structured JSON.

## (O) Objective
Your task is to output only a JSON object containing a key-value pairs, where:

- the key "result" value is a boolean (true or false) based on whether the input text use deep learning models or methods in their methodology, and
- the key "prose" value is the most salient excerpt from the paper that shows concrete evidence of deep learning usage in the paper or empty if no deep learning method are used.

No explanations or extra output are allowed.

## (S) Style
Responses must be strictly machine-readable JSON. No natural language, commentary, or formatting beyond the JSON object is permitted.

## (T) Tone
Neutral, objective, and machine-like.

## (A) Audience
The audience is a machine system that parses JSON. Human readability is irrelevant.

## (R) Response
Return only a JSON object of the form:

```json
{
    "result": "boolean",
    "prose": "string" | None,
}
```

Nothing else should ever be returned.
"""
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


class UsesDLResponse(BaseModel):
    result: bool
    prose: str | None


class ALCFConnection:
    def __init__(self, api_key: str) -> None:
        self.openai_client: OpenAI = OpenAI(
            api_key=api_key,
            base_url="https://inference-api.alcf.anl.gov/resource_server/sophia/vllm/v1",
        )
        self.model: str = "openai/gpt-oss-120b"

    def query(self, system_prompt: str, user_prompt: str) -> ChatCompletion:
        return self.openai_client.chat.completions.create(
            model="openai/gpt-oss-120b",
            reasoning_effort="high",
            frequency_penalty=0,
            stream=False,
            seed=42,
            n=1,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )


def parse_cli(argv: Optional[list[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="ALCF Inference Tool",
        description="Submit a scientific markdown document to ALCF Sophia completions API",
        epilog="Nicholas M. Synovic",
    )
    parser.add_argument(
        "--api-key",
        required=True,
        help="ALCF inference server API key (Bearer token)",
        type=str,
    )
    parser.add_argument(
        "--prompt-id",
        required=True,
        choices=list(PROMPT_TEMPLATES.keys()),
        help="Which prompt template to use",
    )
    parser.add_argument(
        "--input-md",
        required=True,
        help="Path to Markdown file with scientific prose",
        type=lambda x: Path(x).resolve(),
    )
    parser.add_argument(
        "--output-json",
        required=True,
        help="Path to write response JSON (and status)",
        type=lambda x: Path(x).resolve(),
    )
    parser.add_argument(
        "--model",
        default="openai/gpt-oss-120b",
        help="Model name to request",
        type=str,
    )

    return parser.parse_args(argv)


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


def configure_logging(
    log_dir: Path = Path(".").resolve(), level: int = logging.INFO
) -> Path:
    ts: str = datetime.now(tz=timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    log_filename: Path = Path(os.path.join(log_dir, f"alcf_submit_{ts}.log")).resolve()

    # basic file handler + console
    logger: Logger = logging.getLogger()
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


def main(argv: Optional[list[str]] = None) -> int:
    # Set default return code
    rc: int = 0

    # Parse the command line
    args: Namespace = parse_cli(argv)

    # Configure logging
    configure_logging()

    # Mask API key in logs
    logging.info(
        "Using model=%s, prompt_id=%s, input=%s, output=%s",
        args.model,
        args.prompt_id,
        args.input_md,
        args.output_json,
    )
    logging.debug("API key (masked): %s", mask_key(args.api_key))

    # Get system prompt
    system_prompt: str = PROMPT_TEMPLATES[args.prompt_id]
    logging.info("Loaded system prompt: %s", args.prompt_id)

    # Validate input markdown file
    if not args.input_md.is_file():
        logging.error("Input markdown file not found: %s", args.input_md)
        return 2
    else:
        markdown_text: str = args.input_md.read_text(encoding="utf-8")
        logging.info("Loaded user prompt: %s", args.input_md)

    # Connect to the inference service
    oc: ALCFConnection = ALCFConnection(api_key=args.api_key)
    logging.info("Connected to the ALCF inference server")

    # Submit content for analysis
    logging.info("Sent request")
    start_time: float = time()
    resp: ChatCompletion = oc.query(
        system_prompt=system_prompt,
        user_prompt=markdown_text,
    )
    end_time: float = time()
    logging.info(f"Response generated in {end_time - start_time} seconds")

    # Handle completions
    message_json: dict = loads(s=resp.choices[0].message.content)
    logging.info("Writing JSON to %s", args.output_json)
    dump(obj=message_json, fp=args.output_json.open(mode="w"), indent=4)

    logging.info("Finished with return code %d", rc)
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
