#!/usr/bin/env python3

import os

from openai import OpenAI

CANCELABLE_BATCH_STATUSES = {
    "validating",
    "in_progress",
    "finalizing",
}


def delete_all_files(client: OpenAI) -> None:
    print("Fetching files...")

    files = client.files.list()

    if not files.data:
        print("No files found.")
        return

    for file_obj in files.data:
        file_id = file_obj.id

        try:
            print(f"Deleting file: {file_id}")
            client.files.delete(file_id)
            print(f"Deleted file: {file_id}")
        except Exception as exc:
            print(f"Failed to delete file {file_id}: {exc}")


def cancel_all_batches(client: OpenAI) -> None:
    print("Fetching batches...")

    batches = client.batches.list()

    if not batches.data:
        print("No batches found.")
        return

    for batch in batches.data:
        batch_id = batch.id
        status = batch.status

        if status in CANCELABLE_BATCH_STATUSES:
            try:
                print(f"Cancelling batch: {batch_id} ({status})")
                client.batches.cancel(batch_id)
                print(f"Cancelled batch: {batch_id}")
            except Exception as exc:
                print(f"Failed to cancel batch {batch_id}: {exc}")
        else:
            print(f"Skipping batch: {batch_id} (status={status}, not cancelable)")


def main() -> None:
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise RuntimeError("OPENAI_API_KEY environment variable is not set.")

    client = OpenAI(api_key=api_key)

    print("\n=== Deleting Files ===")
    delete_all_files(client)

    print("\n=== Cancelling Batches ===")
    cancel_all_batches(client)

    print("\nDone.")


if __name__ == "__main__":
    main()
