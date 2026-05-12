#!/usr/bin/env python3

import os
from pathlib import Path
from typing import Iterable

from openai import OpenAI


def upload_files(
    file_paths: Iterable[str],
    purpose: str = "batch",
) -> list[str]:
    """
    Upload files to OpenAI.

    Args:
        file_paths: Iterable of file paths
        purpose: OpenAI file purpose
                 ("batch", "fine-tune", "assistants", "user_data", etc.)

    Returns:
        List of uploaded file IDs
    """

    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise RuntimeError("OPENAI_API_KEY environment variable is not set.")

    client = OpenAI(api_key=api_key)

    uploaded_file_ids = []

    for file_path in file_paths:
        path = Path(file_path)

        if not path.exists():
            print(f"Skipping missing file: {path}")
            continue

        if not path.is_file():
            print(f"Skipping non-file: {path}")
            continue

        try:
            print(f"Uploading: {path}")

            with open(path, "rb") as f:
                uploaded_file = client.files.create(
                    file=f,
                    purpose=purpose,
                )

            uploaded_file_ids.append(uploaded_file.id)

            print(f"Uploaded {path.name} -> {uploaded_file.id}")

        except Exception as exc:
            print(f"Failed to upload {path}: {exc}")

    return uploaded_file_ids


def upload_directory(
    directory: str,
    extension_filter: str | None = None,
    purpose: str = "batch",
) -> list[str]:
    """
    Upload all files in a directory.

    Args:
        directory: Directory containing files
        extension_filter: Optional extension filter
                         Example: ".jsonl"
        purpose: OpenAI file purpose
    """

    directory_path = Path(directory)

    if not directory_path.exists():
        raise FileNotFoundError(f"Directory does not exist: {directory}")

    files = []

    for file_path in directory_path.iterdir():
        if not file_path.is_file():
            continue

        if extension_filter and file_path.suffix != extension_filter:
            continue

        files.append(str(file_path))

    return upload_files(
        file_paths=files,
        purpose=purpose,
    )


if __name__ == "__main__":
    # Example 1: Upload specific files
    # upload_files(
    #     [
    #         "batch_001.jsonl",
    #         "batch_002.jsonl",
    #     ],
    #     purpose="batch",
    # )

    # Example 2: Upload all JSONL files in a folder
    uploaded_ids = upload_directory(
        directory="../data/batches",
        extension_filter=".jsonl",
        purpose="batch",
    )

    print("\nUploaded file IDs:")
    for file_id in uploaded_ids:
        print(file_id)
