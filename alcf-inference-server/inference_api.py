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

import pandas
from mdformat import text
from openai import OpenAI
from openai.types.chat.chat_completion import ChatCompletion
from pandas import DataFrame
from progress.bar import Bar
from sqlalchemy import Engine, create_engine


class ALCFConnection:
    def __init__(self, api_key: str) -> None:
        self.openai_client: OpenAI = OpenAI(
            api_key=api_key,
            base_url="https://inference-api.alcf.anl.gov/resource_server/sophia/vllm/v1",
        )
        self.model: str = "openai/gpt-oss-120b"

    def query(
        self,
        system_prompt: str,
        user_prompt: str,
        user_prompt_tokens: int,
    ) -> ChatCompletion:
        max_tokens: int = user_prompt_tokens + 10000

        logging.info("Sent request of %d tokens", max_tokens)
        return self.openai_client.chat.completions.create(
            model="openai/gpt-oss-120b",
            reasoning_effort="high",
            max_tokens=max_tokens,
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
        choices=["uses_dl", "uses_ptms"],
        help="Which prompt template to use",
    )
    parser.add_argument(
        "--db",
        required=True,
        help="Path to SQLite3 database",
        type=lambda x: Path(x).resolve(),
    )
    parser.add_argument(
        "--model",
        default="openai/gpt-oss-120b",
        help="Model name to request",
        type=str,
    )

    return parser.parse_args(argv)


def configure_logging(
    log_dir: Path = Path(".").resolve(),
    level: int = logging.INFO,
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

    logging.info("Logging to %s", log_filename)
    return log_filename


def mask_key(key: str, show_last: int = 4) -> str:
    if not key:
        return "<empty>"
    if len(key) <= show_last:
        return "*" * len(key)
    return "*" * (len(key) - show_last) + key[-show_last:]


def get_system_prompt(db_engine: Engine, prompt_tag: str) -> str:
    sql_query: str = f"""
    SELECT
        llm_prompts.prompt
    FROM
        llm_prompts
    WHERE
        llm_prompts.tag = "{prompt_tag}";
    """

    return pandas.read_sql_query(sql=sql_query, con=db_engine).reset_index()["prompt"][
        0
    ]


def get_user_prompts(db_engine: Engine) -> DataFrame:
    sql_query: str = f"""
    SELECT
        plos_natural_science_paper_content.plos_paper_id,
        plos_natural_science_paper_content.formatted_md,
        plos_natural_science_paper_content.formatted_md_token_count
    FROM
    	plos_natural_science_paper_content;
    """

    return pandas.read_sql_query(sql=sql_query, con=db_engine)


def submit_request(
    alcf_connection: ALCFConnection,
    system_prompt: str,
    user_prompt: str,
    user_prompt_token_count: int,
) -> dict:
    # Submit content for analysis
    start_time: float = time()
    resp: ChatCompletion = alcf_connection.query(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        user_prompt_tokens=user_prompt_token_count,
    )
    end_time: float = time()
    logging.info(f"Response generated in {end_time - start_time} seconds")

    # Handle completions
    return loads(s=resp.choices[0].message.content)


def main(argv: Optional[list[str]] = None) -> int:
    # Set default return code
    rc: int = 0

    # Parse the command line
    args: Namespace = parse_cli(argv)

    # Configure logging
    configure_logging()

    # Mask API key in logs
    logging.info(
        "Using model=%s, prompt_id=%s, db=%s",
        args.model,
        args.prompt_id,
        args.db,
    )
    logging.debug("API key (masked): %s", mask_key(args.api_key))

    # Create database engine
    db_engine: Engine = create_engine(url=f"sqlite:///{args.db}")

    # Get system prompt
    system_prompt: str = get_system_prompt(
        db_engine=db_engine,
        prompt_tag=args.prompt_id,
    )
    logging.info("Loaded system prompt: %s", args.prompt_id)

    # Connect to the inference service
    oc: ALCFConnection = ALCFConnection(api_key=args.api_key)
    logging.info("Connected to the ALCF inference server")

    # Get user prompts
    user_prompts: DataFrame = get_user_prompts(db_engine=db_engine)
    logging.info("Loaded user prompts: %d", user_prompts.shape[0])

    with Bar("Submitting queries...", max=user_prompts.shape[0]) as bar:
        _df: DataFrame
        for _, _df in user_prompts.iterrows():
            plos_paper_id: int = _df["plos_paper_id"]
            user_prompt: str = _df["formatted_md"]
            user_prompt_token_count: int = int(_df["formatted_md_token_count"])

            message_json: dict = submit_request(
                alcf_connection=oc,
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                user_prompt_token_count=user_prompt_token_count,
            )

            output_fp: Path = Path(f"{plos_paper_id}_{args.prompt_id}.json").resolve()
            logging.info("Writing JSON to %s", output_fp)

            dump(
                obj=message_json,
                fp=output_fp.open(mode="w"),
                indent=4,
            )

            bar.next()

    logging.info("Finished with return code %d", rc)
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
