from requests import Session
from requests.adapters import HTTPAdapter, Retry


class HTTPSession:
    def __init__(self) -> None:
        self.timeout: int = 3600
        self.max_retries: int = 10

        self.session: Session = Session()
        self.session.mount(
            "https://",
            HTTPAdapter(
                max_retries=Retry(
                    total=10,
                    backoff_factor=1,
                    status_forcelist=[403, 429, 500, 502, 503, 504],
                    allowed_methods=["HEAD", "GET", "OPTIONS", "POST"],
                ),
            ),
        )
