from requests import Response, Session
from requests.adapters import HTTPAdapter, Retry


class HTTPSession:
    """HTTP session manager with retry logic for scientific web requests.

    Provides a configured requests Session with automatic retries for common
    HTTP status codes and methods for DOI resolution. This class is designed
    for robust web scraping and API interactions in scientific research
    applications where network reliability is critical.

    Attributes:
        timeout (int): Default timeout for HTTP requests in seconds (3600s).
        max_retries (int): Maximum number of retry attempts for failed requests (10).
        session (requests.Session): Configured requests session with retry adapter.

    Example:
        >>> http_session = HTTPSession()
        >>> resolved_url = http_session.resolve_doi("10.1038/nature12373")
        >>> print(resolved_url)
        https://www.nature.com/articles/nature12373

    Note:
        The session automatically retries on HTTP status codes: 403, 429, 500, 502, 503, 504
        with exponential backoff. Only HEAD, GET, OPTIONS, and POST methods are retried.
    """

    def __init__(self) -> None:
        """Initialize HTTP session with retry configuration.

        Sets up a requests Session with retry logic for failed HTTP requests.
        Configures automatic retries for common server error status codes
        with exponential backoff.

        The session is configured with:
        - 3600 second default timeout for HTTP requests
        - Maximum 10 retry attempts with 1-second backoff factor
        - Retries enabled for status codes: 403, 429, 500, 502, 503, 504
        - Retries allowed for methods: HEAD, GET, OPTIONS, POST

        Returns:
            None

        Side Effects:
            - Sets instance attributes: timeout, max_retries, session
            - Configures HTTPS adapter with retry logic
        """
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

    def resolve_doi(self, doi_id: str) -> str:
        """Resolve a Digital Object Identifier (DOI) to its target URL.

        Performs a HEAD request to the DOI resolver to get the final URL
        after following all redirects. This method is useful for obtaining
        direct links to scientific papers from their DOI identifiers.

        Args:
            doi_id (str): The DOI identifier to resolve (e.g., "10.1038/nature12373").

        Returns:
            str: The resolved URL pointing to the actual resource.

        Raises:
            requests.exceptions.RequestException: If the HTTP request fails
                due to network issues, timeouts, or server errors.
            requests.exceptions.Timeout: If the request times out after 60 seconds.

        Example:
            >>> session = HTTPSession()
            >>> url = session.resolve_doi("10.1038/nature12373")
            >>> print(url)
            https://www.nature.com/articles/nature12373

        Note:
            Uses a 60-second timeout specifically for DOI resolution requests,
            which is shorter than the default session timeout to avoid blocking
            on slow DOI resolver responses.
        """
        doi_url: str = f"https://doi.org/{doi_id}"
        resp: Response = self.session.head(
            url=doi_url,
            timeout=60,
            allow_redirects=True,
        )
        return resp.url
