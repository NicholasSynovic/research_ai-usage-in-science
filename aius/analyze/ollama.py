from logging import Logger
from time import time

from progress.bar import Bar
from requests import Response

from aius.analyze.backend import Backend
from aius.analyze.data_models import Document, ModelResponse


class Ollama(Backend):
    def __init__(
        self,
        name: str,
        logger: Logger,
        ollama_endpoint: str,
        model_name: str = "gpt-oss:20b",
        max_context_tokens: int = 100000,
        max_predict_tokens: int = 10000,
        **kwargs,
    ) -> None:
        super().__init__(name=name, logger=logger, model_name=model_name)

        self.ollama_endpoint: str = f"http://{ollama_endpoint}/api/generate"

        self.max_context_tokens: int = max_context_tokens
        self.max_predict_tokens: int = max_predict_tokens

        self.json_data: dict = {
            "model": self.model_name,
            "stream": False,
            "prompt": "",
            "system": "",
            "keep_alive": "30m",
            "options": {
                "temperature": 0.1,
                "top_k": 1,
                "top_p": 0.1,
                "num_predict": self.max_predict_tokens,
                "num_ctx": self.max_context_tokens,
                "seed": 42,
            },
        }

    def inference_document(
        self,
        document: Document,
        system_prompt: str,
    ) -> ModelResponse:
        json_data: dict = self.json_data.copy()
        json_data["prompt"] = document.content
        json_data["system"] = system_prompt

        start_time: float = time()
        self.logger.info("Sending query to ALCF sophia server...")

        resp: Response = self.session.post(
            url=self.ollama_endpoint,
            timeout=self.timeout,
            json=json_data,
        )

        end_time: float = time()

        return ModelResponse(
            doi=document.doi,
            system_prompt=system_prompt,
            user_prompt=document.content,
            model_response=resp.content.decode(),
            model_reasoning="",
            compute_time_seconds=end_time - start_time,
        )

    def inference_doucments(
        self,
        documents: list[Document],
        system_prompt: str,
    ) -> list[ModelResponse]:
        data: list[ModelResponse] = []

        with Bar(f"Inferencing on documents...", max=len(documents)) as bar:
            document: Document
            for document in documents:
                self.logger.debug("Inferencing content from DOI: %s", document.doi)
                response: ModelResponse = self.inference_document(
                    document=document,
                    system_prompt=system_prompt,
                )
                data.append(response)

                bar.next()

        return data
