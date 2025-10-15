import argparse
import io
import json
import re
import zipfile
from json.decoder import JSONDecodeError
from pathlib import Path
from typing import Any

import pandas as pd

_nonprintable_re = re.compile(
    r"[^\x09\x0A\x0D\x20-\x7E]"
)  # allow TAB, LF, CR, and printable ASCII


def _clean_input(s: str) -> str:
    """
    Remove non-printable/control characters that commonly corrupt JSON,
    but keep TAB, LF, CR and printable ASCII.
    """
    return _nonprintable_re.sub("", s)


def _escape_string(s: str) -> str:
    """
    Escape a Python string using JSON escaping and return the inner content
    (json.dumps wraps with quotes).
    """
    return json.dumps(s, ensure_ascii=False)[1:-1]


def _try_parse_json_string(s: str):
    """
    Try to parse a string s as JSON. If it parses, return the parsed value,
    otherwise raise the original exception so caller can fallback.
    """
    return json.loads(s)


def _process(obj: Any) -> Any:
    """
    Recursively process the loaded JSON object:
    - If a value is a string that itself is valid JSON, parse it and process recursively.
    - Otherwise, escape special characters in strings.
    - For dict keys, produce safe (escaped) keys.
    """
    if isinstance(obj, dict):
        new = {}
        for k, v in obj.items():
            # ensure keys are strings and escaped
            if not isinstance(k, str):
                k_str = str(k)
            else:
                k_str = k
            safe_key = _escape_string(k_str)
            new[safe_key] = _process(v)
        return new

    if isinstance(obj, list):
        return [_process(x) for x in obj]

    if isinstance(obj, str):
        s = obj.strip()
        # Quick heuristic: only attempt parse if it looks like JSON-ish
        if (
            s and s[0] in '{["-0123456789tfn'
        ):  # object, array, string, number, true/false/null
            try:
                parsed = _try_parse_json_string(s)
            except Exception:
                # not valid JSON -> escape and return
                return _escape_string(obj)
            else:
                # parsed successfully; recursively process parsed value
                return _process(parsed)
        else:
            # not JSON-like -> just escape
            return _escape_string(obj)

    # numbers, booleans, None leave as-is
    return obj


def robust_json_decode(s: str):
    """
    Robustly decode a JSON string into Python objects while:
      - cleaning non-printables,
      - parsing nested JSON encoded strings,
      - escaping special characters in remaining strings.
    Returns the processed Python object.
    Raises json.JSONDecodeError when the top-level JSON cannot be parsed.
    """
    cleaned = _clean_input(s)
    data = json.loads(cleaned)  # let this raise JSONDecodeError if top-level is invalid
    return _process(data)


def read_parquets_from_zip(zip_path: Path) -> pd.DataFrame:
    """Read all Parquet files from a ZIP archive into one DataFrame."""
    frames = []
    with zipfile.ZipFile(zip_path, "r") as zf:
        for name in zf.namelist():
            if name.endswith(".parquet"):
                with zf.open(name) as f:
                    data = f.read()
                    df = pd.read_parquet(io.BytesIO(data))
                    frames.append(df)
    if not frames:
        raise ValueError(f"No Parquet files found in {zip_path}")
    return (
        pd.concat(frames, ignore_index=True)
        .sort_values(by="plos_prompt_enineering_paper_id")
        .reset_index(drop=True)
    )


def parse_response(df: pd.DataFrame) -> pd.Series:
    data: list[dict] = []

    df["json"] = df["response_text"].apply(json.loads)

    for _, row in df.iterrows():
        datum = robust_json_decode(s=row["json"]["response"])

        data.append(datum)

    return pd.Series(data=data)


def main():
    parser = argparse.ArgumentParser(
        description="Read all Parquet files from a ZIP archive into a single DataFrame"
    )
    parser.add_argument(
        "--zipfile",
        type=Path,
        help="Path to ZIP file containing Parquet files",
    )
    args = parser.parse_args()

    df = read_parquets_from_zip(args.zipfile)

    print(df[df["plos_prompt_enineering_paper_id"] == 75])
    quit()

    df["json_response"] = parse_response(df=df)

    df["json_response"].to_json(path_or_buf="review.json", indent=4, index=False)


if __name__ == "__main__":
    main()
