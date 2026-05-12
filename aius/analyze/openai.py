from logging import Logger
from time import time

from openai import OpenAI
from openai.types.responses.response import Response
from progress.bar import Bar

from aius.analyze.backend import Backend
from aius.analyze.data_models import Document, ModelResponse


class OpenAIBackend(Backend):
    def __init__(
        self,
        logger: Logger,
        auth_key: str,
        model_name: str = "gpt-5.4-nano-2026-03-17",
        **kwargs,
    ) -> None:
        super().__init__(name="openai", logger=logger, model_name=model_name)

        self.openai_client: OpenAI = OpenAI(
            api_key=auth_key,
            timeout=self.timeout,
            max_retries=self.max_retries,
        )

    def inference_document(
        self,
        document: Document,
        system_prompt: str,
    ) -> ModelResponse:
        start_time: float = time()

        self.logger.info("Sending query to OpenAI Responses API...")

        try:
            resp: Response = self.openai_client.responses.create(
                input=[
                    {
                        "role": "system",
                        "content": system_prompt,
                    },
                    {
                        "role": "user",
                        "content": document.content,
                    },
                ],
                max_output_tokens=20000,
                model=self.model_name,
                reasoning={
                    "effort": "high",
                    "summary": "detailed",  # optional
                },
                stream=False,
                text={
                    "format": {
                        "type": "json_object",
                    }
                },
                timeout=self.timeout,
            )

        except Exception as error:
            self.logger.error(
                "OpenAI request failed for DOI %s: %s",
                document.doi,
                error,
            )

            end_time: float = time()

            return ModelResponse(
                doi=document.doi,
                system_prompt=system_prompt,
                user_prompt=document.content,
                model_response="",
                model_reasoning="",
                compute_time_seconds=end_time - start_time,
            )

        end_time: float = time()

        # Final model output
        model_response: str = resp.output_text or ""

        # Reasoning summary (not chain-of-thought)
        model_reasoning: str = ""

        try:
            output_item: object
            for output_item in resp.output:
                if getattr(output_item, "type", None) == "reasoning":
                    summaries = getattr(output_item, "summary", [])
                    if summaries:
                        model_reasoning = "\n".join(
                            item.text for item in summaries if hasattr(item, "text")
                        )
                    break

        except Exception as error:
            self.logger.debug(
                "No reasoning summary for DOI %s: %s",
                document.doi,
                error,
            )

        return ModelResponse(
            doi=document.doi,
            system_prompt=system_prompt,
            user_prompt=document.content,
            model_response=model_response,
            model_reasoning=model_reasoning,
            compute_time_seconds=end_time - start_time,
        )

    def inference_documents(
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
