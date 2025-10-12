from mdformat import text
from requests import Response, post

from aius import POST_TIMEOUT


class PandocAPI:
    def __init__(self, pandoc_url: str = "http://localhost:3030") -> None:
        # Set global class variables
        self.pandoc_url: str = pandoc_url
        self.json_body: dict[str, str] = {"from": "jats", "to": "markdown"}

    def convert_jats_to_md(self, jats_xml: str) -> str:
        # Add JATS XML content to the body of the JSON object
        self.json_body["text"] = jats_xml

        # Submit POST request
        resp: Response = post(
            url=self.pandoc_url,
            json=self.json_body,
            timeout=60,
        )

        # Parse and format POST response
        return text(md=resp.content.decode(encoding="utf-8"))
