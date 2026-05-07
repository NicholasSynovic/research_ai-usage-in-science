from abc import ABC, abstractmethod
from logging import Logger

from requests import Session

from aius.analyze.data_models import Document, ModelResponse
from aius.util.http_session import HTTPSession


class Backend(ABC):
    def __init__(
        self,
        name: str,
        logger: Logger,
        model_name: str,
        max_retries: int = 100,
        timeout: int = 3600,
        **kwargs,
    ) -> None:
        self.name: str = name
        self.logger: Logger = logger
        self.model_name: str = model_name

        session_util: HTTPSession = HTTPSession()

        self.timeout: int = timeout
        session_util.timeout = self.timeout

        self.max_retries: int = max_retries
        session_util.max_retries = self.max_retries

        self.session: Session = session_util.session

    @abstractmethod
    def inference_document(
        self,
        document: Document,
        system_prompt: str,
    ) -> ModelResponse: ...

    @abstractmethod
    def inference_documents(
        self,
        documents: list[Document],
        system_prompt: str,
    ) -> list[ModelResponse]: ...
