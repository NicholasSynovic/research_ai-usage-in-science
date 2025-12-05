from logging import Logger

from openai import OpenAI
from openai.types.chat import ChatCompletion
from progress.bar import Bar

from aius.db import DB
from aius.inference import Inference
from aius.inference.models import Document, ModelResponse, UsesDL


class ALCF(Inference):
    def __init__(self, logger: Logger, db: DB, prompt_id: str, alcf_auth_token: str, model: str = "openai/gpt-oss-120b",) -> None:
        self.logger: Logger = logger
        self.db: DB = db
        self.prompt_id: str = prompt_id
        self.model: str = model

        self.openai_client: OpenAI = OpenAI(
            api_key=alcf_auth_token,
            base_url="https://inference-api.alcf.anl.gov/resource_server/sophia/vllm/v1",
        )

    def inference_document(self, system_prompt: str, document: Document) -> ChatCompletion:
        ...

    def inference_documents(self, system_prompt: str, documents: list[Document]) -> list[ModelResponse]::
        ...

    def parse_uses_dl(self, responses: list[ModelResponse]) -> list[UsesDL]:
        ...
