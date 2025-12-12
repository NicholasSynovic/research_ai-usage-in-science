from abc import ABC, abstractmethod
from logging import Logger

from requests import Session

from aius.analyze import Document, ModelResponse
from aius.util.http_session import HTTPSession


class Backend(ABC):
    def __init__(self, name: str, logger: Logger, model_name: str) -> None:
        self.name: str = name
        self.logger: Logger = logger
        self.model_name: str = model_name

        session_util: HTTPSession = HTTPSession()
        self.timeout: int = session_util.timeout
        self.session: Session = session_util.session
        self.max_retries: int = session_util.max_retries

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
