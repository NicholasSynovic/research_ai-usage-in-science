import argparse
import json
from collections import defaultdict
from json import dumps, load, loads
from pathlib import Path
from sqlite3 import Connection, connect

import pandas as pd
from progress.bar import Bar

from aius.analyze.data_models import Document, ModelResponse


def load_doc_map(fp: str) -> dict[str, str]:
    return load(open(fp))


def process_jsonl_files(input_dir) -> list[dict]:
    """
    Reads all .jsonl files in the given directory and loads
    each line into a list of dictionaries.
    """
    data_path = Path(input_dir)

    # Check if the directory exists
    if not data_path.is_dir():
        print(f"Error: The directory {input_dir} does not exist.")
        return []

    all_records = []

    # Iterate through all .jsonl files in the directory
    for file_path in data_path.glob("*.jsonl"):
        # print(f"Processing: {file_path.name}")

        with file_path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:  # Skip empty lines
                    try:
                        record = json.loads(line)
                        all_records.append(record)
                    except json.JSONDecodeError as e:
                        print(f"Skipping malformed line in {file_path.name}: {e}")

    # print(f"Successfully loaded {len(all_records)} records.")
    return all_records


def records_to_model(records: list[dict]) -> list[ModelResponse]:
    data: list[ModelResponse] = []

    with Bar("Loading records into ModelResponses...", max=len(records)) as bar:
        for record in records:
            doi: str = record["custom_id"]

            try:
                model_reasoning: str = dumps(
                    record["response"]["body"]["output"][0]["summary"][0]["text"]
                )
            except KeyError, IndexError:
                model_reasoning: str = ""

            try:
                model_response: str = record["response"]["body"]["output"][1][
                    "content"
                ][0]["text"]
            except IndexError:
                model_response: str = record["response"]["body"]["output"][0][
                    "content"
                ][0]["text"]

            compute_time: float = (
                record["response"]["body"]["completed_at"]
                - record["response"]["body"]["created_at"]
            )

            data.append(
                ModelResponse(
                    doi=doi,
                    system_prompt="",
                    user_prompt="",
                    model_reasoning=model_reasoning,
                    model_response=model_response,
                    compute_time_seconds=compute_time,
                )
            )
            bar.next()

    return data


def add_model_doi(
    doc_map: dict[str, str], models: list[ModelResponse]
) -> list[ModelResponse]:
    data: list[ModelResponse] = []

    model: ModelResponse
    for model in models:
        model.doi = doc_map[model.doi]
        data.append(model)

    return data


def add_model_user_prompt(
    db: Connection,
    models: list[ModelResponse],
) -> list[ModelResponse]:
    data: list[ModelResponse] = []

    markdown_df: pd.DataFrame = pd.read_sql_query(
        sql="SELECT doi, markdown FROM markdown",
        con=db,
    )

    model: ModelResponse
    for model in models:
        model.user_prompt = markdown_df[markdown_df["doi"] == model.doi][
            "markdown"
        ].tolist()[0]
        data.append(model)

    return data


def convert(models: list[ModelResponse]) -> pd.DataFrame:
    return pd.concat(objs=[model.to_df for model in models])


def main():
    # 1. Initialize the parser
    parser = argparse.ArgumentParser(
        description="Read a directory of JSONL files into Python dictionaries."
    )

    # 2. Add arguments
    parser.add_argument(
        "input_dir", type=str, help="Path to the directory containing .jsonl files"
    )
    parser.add_argument(
        "--doc",
        type=str,
        help="Path to the doc map",
        required=True,
    )
    parser.add_argument(
        "--db",
        type=str,
        help="Path to the db",
        required=True,
    )

    # 3. Parse the arguments
    args = parser.parse_args()

    db: Connection = connect(database=args.db)

    # 4. Load the document map
    doc_map: dict[str, str] = load_doc_map(fp=args.doc)

    # 5. Load the JSONL files
    records = process_jsonl_files(args.input_dir)

    # 6. Convert records to models
    models: list[ModelResponse] = records_to_model(records=records)

    # 7. Fix metadata with the doc_map
    models = add_model_doi(doc_map=doc_map, models=models)

    # 8. Add content from the server
    models = add_model_user_prompt(db=db, models=models)

    # 9. Convert to DataFrame
    df: pd.DataFrame = convert(models=models)

    df.to_parquet(path="jsonl.parquet", engine="auto")
    db.close()


if __name__ == "__main__":
    main()
