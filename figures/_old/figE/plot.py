from pathlib import Path
from string import Template

import click
import matplotlib.pyplot as plt
import pandas
import seaborn as sns
from pandas import DataFrame
from progress.bar import Bar
from requests import Response, Session
from requests.adapters import HTTPAdapter, Retry

from aius import FIELD_FILTER

# Create a Requests Session that implements expontial backoff
SESSION: Session = Session()
RETRIES = Retry(total=5, backoff_factor=1)
SESSION.mount("https://", HTTPAdapter(max_retries=RETRIES))


def get_oa_topic_api_responses() -> list[Response]:
    # Data strcture to store responses
    data: list[Response] = []

    # Set defaults based on OpenAlex constants
    oa_topic_api_pages: int = 46
    oa_topic_api_template: Template = Template(
        template="https://api.openalex.org/topics?per_page=100&page=${page}",
    )

    # For each OpenAlex topic API page, get the HTTP GET response for future
    # parsing
    with Bar(
        "Getting OpenAlex Topic API Responses...",
        max=oa_topic_api_pages,
    ) as bar:
        page_num: int
        for page_num in range(1, oa_topic_api_pages):
            url: str = oa_topic_api_template.substitute(page=page_num)
            resp: Response = SESSION.get(url=url, timeout=60)
            data.append(resp)
            bar.next()

    return data


# From OpenAlex topic API page get the field number of each topic
def get_oa_topic_field_from_response(resps: list[Response]) -> dict[str, int]:
    # Data structure to store data
    data: dict[str, int] = {}

    with Bar(
        "Extracting field numbers from topic responses...",
        max=len(resps),
    ) as bar:
        resp: Response
        for resp in resps:
            # Get the response JSON
            json_data: dict = resp.json()

            # Iterate through the topics and extract the name and field number
            topic: dict
            for topic in json_data["results"]:  # A list of dicts for each topic
                field_dict: dict[str, str] = topic["field"]
                field_name: str = field_dict["display_name"]
                field_num: int = int(field_dict["id"].split(sep="/")[-1])
                data[field_name] = field_num

            bar.next()

    return data


# For each field, get the total number of works for that field
def get_oa_field_works(field_name_number: dict[str, int]) -> DataFrame:
    # Create the data structure
    data: dict[str, list[str | int]] = {
        "field_name": [],
        "field_num": [],
        "field_works": [],
    }

    # Set defaults based on OpenAlex constants
    oa_field_api_template: Template = Template(
        template="https://api.openalex.org/fields/${field_number}"
    )

    # For each OpenAlex field, extract the works for each OpenAlex Field
    with Bar(
        "Getting OpenAlex Topic API Responses...",
        max=len(field_name_number.keys()),
    ) as bar:
        field_name: str
        field_num: int
        for field_name, field_num in field_name_number.items():
            url: str = oa_field_api_template.substitute(field_number=field_num)
            resp: Response = SESSION.get(url=url, timeout=60)
            field_works: int = resp.json()["works_count"]

            data["field_name"].append(field_name)
            data["field_num"].append(field_num)
            data["field_works"].append(field_works)

            bar.next()

    return DataFrame(data=data)


def plot(df: DataFrame) -> None:
    sns.barplot(data=df, x="field_name", y="field_works")
    plt.title(label="Number Of Natural Science Works Indexed By OpenAlex")
    plt.xlabel(xlabel="OpenAlex Field")
    plt.ylabel(ylabel="Number Of Works")

    plt.xticks(rotation=45, ha="right")

    plt.tight_layout()
    plt.savefig("figE.pdf")


@click.command()
@click.option(
    "-i",
    "--input-fp",
    required=False,
    type=lambda x: Path(x).resolve(),
    default=Path("openalex_field_works.parquet"),
    help="Path to OpenAlex Field Works Apache Parquet file",
)
def main(input_fp: Path) -> None:
    oa_field_data: DataFrame
    if input_fp.exists():
        oa_field_data = pandas.read_parquet(path=input_fp, engine="pyarrow")
    else:
        # Get all OpenAlex topic API responses
        oa_topic_api_responses: list[Response] = get_oa_topic_api_responses()
        # Extract field names and numbers from topic responses
        oa_field_names_numbers: dict[str, int] = get_oa_topic_field_from_response(
            resps=oa_topic_api_responses,
        )
        # Get the works for each field
        oa_field_data: DataFrame = get_oa_field_works(
            field_name_number=oa_field_names_numbers,
        )
        # Write data to file
        oa_field_data.to_parquet(path=Path(input_fp), engine="pyarrow")

    # Get only the natural science fields
    oa_field_data = oa_field_data[
        oa_field_data["field_name"].isin(FIELD_FILTER)
    ].sort_values(
        by="field_works",
        ascending=False,
        ignore_index=True,
    )

    # Get the PLOS papers
    plot(df=oa_field_data)


if __name__ == "__main__":
    main()
