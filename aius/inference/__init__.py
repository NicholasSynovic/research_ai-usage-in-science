from abc import ABC, abstractmethod

from openai.types.chat import ChatCompletion

from aius.inference.models import Document, ModelResponse, UsesDL


class Inference(ABC):
    def __init__(self) -> None:
        pass

    @abstractmethod
    def inference_document(
        self,
        system_prompt: str,
        document: Document,
    ) -> ChatCompletion: ...

    @abstractmethod
    def inference_documents(
        self,
        system_prompt: str,
        documents: list[Document],
    ) -> list[ModelResponse]: ...

    @abstractmethod
    def parse_uses_dl(self, responses: list[ModelResponse]) -> list[UsesDL]: ...
