from logging import Logger
from time import time

import pandas as pd
from openai import InternalServerError, OpenAI
from openai.types.chat.chat_completion import ChatCompletion
from progress.bar import Bar

from aius.analysis import Document, ModelResponse
from aius.analysis.backend import Backend


class Metis(Backend):
    def __init__(
        self,
        logger: Logger,
        auth_key: str,
        model_name: str = "openai/gpt-oss-20b",
    ) -> None:
        super().__init__(name="alcf_metis", logger=logger)

        self.model_name: str = model_name

        self.openai_client: OpenAI = OpenAI(
            api_key=auth_key,
            base_url="https://inference-api.alcf.anl.gov/resource_server/metis/vllm/v1",
            timeout=self.timeout,
            max_retries=self.max_retries,
        )

    def inference_document(
        self,
        document: Document,
        system_prompt: str,
    ) -> ModelResponse:
        start_time: float = time()
        self.logger.info("Sending query to ALCF sophia server...")
        try:
            resp: ChatCompletion = self.openai_client.chat.completions.create(
                model=self.model_name,
                reasoning_effort="high",
                frequency_penalty=0,
                stream=False,
                seed=42,
                n=1,
                temperature=0.1,
                top_p=0.1,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": document.content},
                ],
            )
        except InternalServerError:
            self.logger.error("Internal server error raised with DOI: %s", document.doi)
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

        model_response: str = resp.choices[0].message.content

        model_reasoning: str = ""
        try:
            model_reasoning = resp.choices[0].message.reasoning_content
        except AttributeError:
            self.logger.error("No reasoning output for DOI: %s", document.doi)
            pass

        return ModelResponse(
            doi=document.doi,
            system_prompt=system_prompt,
            user_prompt=document.content,
            model_response=model_response,
            model_reasoning=model_reasoning,
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
