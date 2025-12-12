from itertools import islice
from logging import Logger
from time import time

import pandas as pd
from openai import InternalServerError, OpenAI
from openai.types.chat.chat_completion import ChatCompletion
from pandas import DataFrame, Series
from progress.bar import Bar

from aius.inference.inference_backend import InferenceBackend
from aius.inference.models import Document, ModelResponse


class ALCF(InferenceBackend):
    def __init__(
        self,
        logger: Logger,
        index: int,
        stride: int,
        auth_key: str,
        model_name: str = "openai/gpt-oss-20b",
    ) -> None:
        super().__init__(logger=logger, index=index, stride=stride)

        self.name = "ALCF inference server"
        self.model_name: str = model_name

        self.openai_client: OpenAI = OpenAI(
            api_key=auth_key,
            base_url="https://inference-api.alcf.anl.gov/resource_server/sophia/vllm/v1",
            timeout=3600,
            max_retries=10,
        )

    def inference_single_document(
        self,
        document: Document,
        system_prompt: str,
    ) -> ModelResponse:
        start_time: float = time()
        self.logger.info("Sending query to inference server...")
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
        system_prompt: str,
        document_iterator: islice,
        document_count: int,
    ) -> DataFrame:
        data: list[DataFrame] = []

        with Bar(f"Inferencing on documents...", max=document_count) as bar:
            row: Series
            for _, row in document_iterator:
                document: Document = Document(
                    doi=row["doi"],
                    content=row["markdown"],
                )
                self.logger.debug("Inferencing content from DOI: %s", document.doi)
                data.append(
                    self.inference_single_document(
                        document=document,
                        system_prompt=system_prompt,
                    ).df
                )
                bar.next()

        return pd.concat(objs=data, ignore_index=True)
