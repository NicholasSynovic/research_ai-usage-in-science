#!/usr/bin/env python3

import os
from datetime import datetime, time
from json import dumps
from pathlib import Path
from zoneinfo import ZoneInfo

from openai import OpenAI
from openai.pagination import SyncCursorPage
from openai.types.batch import Batch

LOCAL_TZ = ZoneInfo("America/Chicago")


def get_batch_file_ids(limit: int = 60) -> list[Batch]:
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise RuntimeError("OPENAI_API_KEY environment variable is not set.")

    client = OpenAI(api_key=api_key)

    now = datetime.now(LOCAL_TZ)

    cutoff = datetime.combine(
        now.date(),
        time(hour=16, minute=0),
        tzinfo=LOCAL_TZ,
    )

    cutoff_timestamp = cutoff.timestamp()

    matching_batches = []

    all_batches: list[Batch] = []
    after = None

    while len(all_batches) < limit:
        page = client.batches.list(
            limit=min(100, limit - len(all_batches)),
            after=after,
        )

        if not page.data:
            break

        all_batches.extend(page.data)

        # No more pages
        if not page.has_more:
            break

        # Cursor = last batch ID from current page
        after = page.data[-1].id

    results = []

    for batch in all_batches[:limit]:
        if batch.created_at >= cutoff_timestamp and batch.status == "completed":
            results.append(batch)

    return results


def download_batch_outputs(
    client: OpenAI,
    batches: list[Batch],
    output_dir: str = "./batch_outputs",
) -> None:
    output_path = Path(output_dir)
    output_path.mkdir(
        parents=True,
        exist_ok=True,
    )

    for batch in batches:
        output_file_id = getattr(
            batch,
            "output_file_id",
            None,
        )

        if not output_file_id:
            print(f"Skipping {batch.id}: no output file yet")
            continue

        try:
            print(f"Downloading {output_file_id} from batch {batch.id}")

            content = client.files.content(output_file_id)

            local_file = output_path / f"{batch.id}.jsonl"

            with open(
                local_file,
                "wb",
            ) as f:
                f.write(content.read())

            print(f"Saved: {local_file}")

        except Exception as exc:
            print(f"Failed to download {output_file_id}: {exc}")


if __name__ == "__main__":
    x = get_batch_file_ids(limit=60)
    download_batch_outputs(
        client=OpenAI(api_key=os.getenv("OPENAI_API_KEY")), batches=x, output_dir="."
    )
