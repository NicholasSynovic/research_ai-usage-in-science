import argparse
import json
from json import dumps, loads
from pathlib import Path
from sqlite3 import Connection, connect

import pandas as pd
from progress.bar import Bar

from aius.analyze.data_models import Document, ModelResponse


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
            doi: str = str(int(record["custom_id"].replace("doc-", "")))

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


def convert(db_conn: Connection, models: list[ModelResponse]) -> pd.DataFrame:
    markdown_df: pd.DataFrame = pd.read_sql_query(
        sql="SELECT _id, doi FROM markdown",
        con=db_conn,
        index_col="_id",
    )

    df: pd.DataFrame = pd.concat(objs=[model.to_df for model in models])
    df["doi"] = df["doi"].map(int)
    df = df.sort_values(by="doi", ignore_index=True)

    temp: pd.DataFrame = markdown_df.merge(
        right=df,
        how="outer",
        left_index=True,
        right_on="doi",
    )
    return temp.drop(columns=["doi", "doi_y"]).rename(columns={"doi_x": "doi"})


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
        "--db",
        type=str,
        help="Path to the database",
        required=True,
    )

    # 3. Parse the arguments
    args = parser.parse_args()

    # 4. Execute logic
    records = process_jsonl_files(args.input_dir)

    models: list[ModelResponse] = records_to_model(records=records)

    db: Connection = connect(database=args.db)
    df: pd.DataFrame = convert(db_conn=db, models=models)
    df.to_parquet(path="jsonl.parquet", engine="auto")
    db.close()


if __name__ == "__main__":
    main()
