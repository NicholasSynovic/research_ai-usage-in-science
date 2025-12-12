"""
Get the most cited paper per search query per year for review.

Copyright 2025 (C) Nicholas M. Synovic

"""

from itertools import product
from pathlib import Path

import pandas as pd
from progress.bar import Bar
from requests import Response, Session
from requests.adapters import HTTPAdapter, Retry

import aius
from aius.search.plos import PLOS

# Custom HTTPS session with exponential backoff enabled
SESSION: Session = Session()
SESSION.mount(
    "https://",
    HTTPAdapter(
        max_retries=Retry(total=5, backoff_factor=1),
    ),
)

OUTPUT_PATH: Path = Path("pilot_study.csv").resolve()


def create_plos_urls() -> list[str]:
    # Instantiate PLOS class
    plos: PLOS = PLOS()

    # Create data structure to store data
    urls: list[str] = []

    # Generate keyword-year pairings
    pairs: product = product(aius.KEYWORD_LIST, aius.YEAR_LIST)

    # Create URLs
    pair: tuple[str, int]
    for pair in pairs:
        urls.append(
            plos._construct_url(year=pair[1], keyword=pair[0], page=1)
            .replace("DATE_NEWEST_FIRST", "MOST_CITED")
            .replace("resultsPerPage=100", "resultsPerPage=1")
        )

    return urls


def get_plos_pages(urls: list[str]) -> pd.DataFrame:
    # Data structure to store results
    data: dict[str, list[str | dict | pd.Timestamp]] = {
        "url": [],
        "json": [],
        "timestamp": [],
    }

    # Query PLOS URL
    with Bar("Getting PLOS pilot study pages...", max=len(urls)) as bar:
        url: str
        for url in urls:
            timestamp: pd.Timestamp = pd.Timestamp.utcnow()

            resp: Response = SESSION.get(
                url=url,
                timeout=60,
            )

            # Write data to data structure
            data["url"].append(url)
            data["json"].append(resp.json())
            data["timestamp"].append(timestamp)

            bar.next()

    return pd.DataFrame(data=data)


def extract_document_doi(plos_response_df: pd.DataFrame) -> pd.DataFrame:
    # Data structure to store DOIs
    data: list[str] = []

    # Make a copy of the DataFrame to edit
    df: pd.DataFrame = plos_response_df.copy()

    row: pd.Series
    for _, row in df.iterrows():
        # Get relevant JSON per response
        json_data: dict = row["json"]["searchResults"]["docs"]

        # If the length of JSON data == 0, append an empty string
        if len(json_data) == 0:
            data.append("")
        else:
            data.append(json_data[0]["id"])

    df["doi"] = data
    return df


def main() -> None:
    # Create PLOS URLs
    urls: list[str] = create_plos_urls()

    # Query PLOS
    plos_responses_df: pd.DataFrame = get_plos_pages(urls=urls)

    # Extract DOIs from responses
    plos_responses_with_dois_df: pd.DataFrame = extract_document_doi(
        plos_response_df=plos_responses_df
    )

    # Save DataFrame to CSV file
    plos_responses_with_dois_df.to_csv(
        path_or_buf=Path("pilot_study.csv").resolve(),
        index=False,
    )


if __name__ == "__main__":
    main()
