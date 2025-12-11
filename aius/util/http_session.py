from requests import Session
from requests.adapters import HTTPAdapter, Retry


class HTTPSession:
    def __init__(self) -> None:
        self.timeout: int = 3600

        self.session: Session = Session()
        self.session.mount(
            "https://",
            HTTPAdapter(
                max_retries=Retry(total=10, backoff_factor=1),
            ),
        )
