from math import ceil
from string import Template

from progress.bar import Bar
from requests import Response, get

from aius import FIELD_FILTER

OA_TOPIC_URL_TEMPLATE: Template = Template(
    template="https://api.openalex.org/topics?per_page=100&page=${page}"
)
OA_FIELD_URL_TEMPLATE: Template = Template(
    template="https://api.openalex.org/fields/${field_number}"
)
PAGES: int = ceil(4516 / 100)
GOOD_STATUS_CODE: int = 200
OA_FIELD_NUMBERS: dict[str, int] = {
    "Agricultural and Biological Sciences": 11,
    "Environmental Science": 23,
    "Earth and Planetary Sciences": 19,
    "Physics and Astronomy": 31,
    "Chemistry": 16,
    "Neuroscience": 28,
    "Immunology and Microbiology": 24,
}
OA_FIELD_WORKS: dict[str, int] = {
    "Agricultural and Biological Sciences": 10328653,
    "Environmental Science": 9191866,
    "Earth and Planetary Sciences": 4290599,
    "Physics and Astronomy": 7186862,
    "Chemistry": 5206967,
    "Neuroscience": 3086383,
    "Immunology and Microbiology": 2108297,
}


def _get_topic_results(page: int) -> list[dict]:
    # Using the OpenAlex topic API, get the JSON data
    url: str = OA_TOPIC_URL_TEMPLATE.substitute(page=page)
    resp: Response = get(url=url, timeout=60)

    if resp.status_code != GOOD_STATUS_CODE:
        raise ValueError(f"Invalid response: {url} {resp.status_code}")

    json: dict = resp.json()
    return json["results"]


def _get_topic_field(topic: dict) -> tuple[str, int] | None:
    # From an OpenAlex topic API result item, extract the field and field number
    topic_field: str = topic["field"]["display_name"]
    topic_number: int = int(topic["field"]["id"].split("/")[-1])
    if topic_field in FIELD_FILTER:
        return (topic_field, topic_number)
    else:
        return None


def identify_topic_field_number() -> dict[str, int]:
    # Create a `dict` of the OpenAlex field and number from the topic API
    data: dict[str, int] = {}

    with Bar("Identifying OpenAlex field numbers...", max=PAGES) as bar:
        page: int
        for page in range(1, PAGES):
            results: list[dict] = _get_topic_results(page=page)

            result: dict
            for result in results:
                field: tuple[str, int] | None = _get_topic_field(topic=result)

                if field is None:
                    continue

                data[field[0]] = field[1]

            bar.next()

    return data


def count_works_per_field() -> dict[str, int]:
    data: dict[str, int] = {}

    with Bar("Getting the works per OpenAlex field...", max=7) as bar:
        key: str
        key_number: int
        for key, key_number in OA_FIELD_NUMBERS.items():
            url: str = OA_FIELD_URL_TEMPLATE.substitute(field_number=key_number)
            resp: Response = get(url=url, timeout=60)

            if resp.status_code != GOOD_STATUS_CODE:
                raise ValueError(f"Invalid response: {url} {resp.status_code}")

            json: dict = resp.json()

            data[key] = json["works_count"]

            bar.next()

    return data


count_works_per_field()
