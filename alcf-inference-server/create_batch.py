#!/usr/bin/env python3
"""
Export PLOS paper contents from a SQLite3 database into
JSON Lines suitable for batch inference or completions APIs.

Usage:
    python export_plos_jsonl.py --db-path /path/to/db.sqlite3 --output out.jsonl
"""

import argparse
import json
import math
import os

from sqlalchemy import create_engine, text

SYSTEM_PROMPT: str = """
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


def parse_args():
    parser = argparse.ArgumentParser(description="Export PLOS papers to JSON Lines")
    parser.add_argument(
        "--db-path",
        required=True,
        help="Path to SQLite3 database file",
    )
    parser.add_argument(
        "--output",
        default="output.jsonl",
        help="Base name for output JSONL file (default: output.jsonl)",
    )
    parser.add_argument(
        "--model",
        default="openai/gpt-oss-120b",
        help="Model name to include in JSON object body",
    )
    return parser.parse_args()


def connect_sqlite(db_path: str):
    """Connect to SQLite3 database via SQLAlchemy."""
    engine = create_engine(f"sqlite:///{db_path}")
    return engine.connect()


def fetch_paper_records(conn):
    """Run the provided SQL query and return all rows."""
    query = text(
        """
        SELECT
            plos_natural_science_paper_content.plos_paper_id,
            plos_natural_science_paper_content.formatted_md,
            plos_natural_science_paper_content.formatted_md_token_count
        FROM
            plos_natural_science_paper_content;
        """
    )
    result = conn.execute(query)
    rows = result.fetchall()
    return rows


def build_json_object(row, model_name: str):
    """Construct a JSON object as described."""
    paper_id, md_text, token_count = row
    max_tokens = int(token_count) + 10_000
    return {
        "custom_id": str(paper_id),
        "method": "POST",
        "url": "/v1/chat/completions",
        "body": {
            "model": model_name,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": md_text},
            ],
            "max_tokens": max_tokens,
        },
    }


def write_jsonl_and_split(records, output_base, chunk_size_mb=10.0):
    """
    Write each record as a JSON line, then split file into chunks ≤ chunk_size_mb.
    """
    temp_path = output_base
    with open(temp_path, "w", encoding="utf-8") as f:
        for obj in records:
            json_line = json.dumps(obj, ensure_ascii=False)
            f.write(json_line + "\n")

    # Split the large file into smaller chunks of ~chunk_size_mb each
    chunk_size_bytes = int(chunk_size_mb * 1024 * 1024)
    file_size = os.path.getsize(temp_path)
    num_chunks = math.ceil(file_size / chunk_size_bytes)

    print(f"Total output size: {file_size / 1_000_000:.2f} MB")
    print(f"Splitting into {num_chunks} chunk(s) of ~{chunk_size_mb} MB each...")

    with open(temp_path, "r", encoding="utf-8") as f:
        chunk_index = 1
        bytes_written = 0
        out = open(
            f"{output_base.replace('.jsonl', '')}_{chunk_index:04d}.jsonl",
            "w",
            encoding="utf-8",
        )

        for line in f:
            line_bytes = len(line.encode("utf-8"))
            if bytes_written + line_bytes > chunk_size_bytes:
                out.close()
                chunk_index += 1
                bytes_written = 0
                out = open(
                    f"{output_base.replace('.jsonl', '')}_{chunk_index:04d}.jsonl",
                    "w",
                    encoding="utf-8",
                )
            out.write(line)
            bytes_written += line_bytes

        out.close()

    os.remove(temp_path)
    print("Done.")


def main():
    args = parse_args()

    if not os.path.exists(args.db_path):
        raise FileNotFoundError(f"Database not found: {args.db_path}")

    print(f"Connecting to {args.db_path}...")
    with connect_sqlite(args.db_path) as conn:
        rows = fetch_paper_records(conn)

    print(f"Fetched {len(rows)} rows.")
    records = [build_json_object(r, args.model) for r in rows]

    print(f"Writing to {args.output} and splitting into 9 MB chunks...")
    write_jsonl_and_split(records, args.output, 9)


if __name__ == "__main__":
    main()
