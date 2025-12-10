from itertools import islice
from json import loads
from logging import Logger
from time import time

import pandas as pd
from openai import OpenAI
from openai.types.chat.chat_completion import ChatCompletion
from pandas import DataFrame, Series
from progress.bar import Bar

from aius.inference.models import Document, ModelResponse


class InferenceBackend:
    def __init__(
        self,
        logger: Logger,
        name: str,
        index: int,
        stride: int,
        auth_key: str,
        openai_endpoint: str,
        model_name: str = "gpt-oss:20b",
        http_timeout: int = 3600,
        http_retries: int = 10,
    ) -> None:
        self.logger: Logger = logger
        self.index: int = index
        self.stride: int = stride
        self.name = name
        self.model_name: str = model_name

        self.openai_client: OpenAI = OpenAI(
            api_key=auth_key,
            base_url=openai_endpoint,
            timeout=http_timeout,
            max_retries=http_retries,
        )

    def inference_single_document(
        self,
        document: Document,
        system_prompt: str,
    ) -> ModelResponse:
        start_time: float = time()
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
        end_time: float = time()

        return ModelResponse(
            doi=document.doi,
            system_prompt=system_prompt,
            user_prompt=document.content,
            model_response=loads(s=resp.choices[0].message.content),
            model_reasoning=resp.choices[0].message.reasoning_content,
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
                data.append(
                    self.inference_single_document(
                        document=document,
                        system_prompt=system_prompt,
                    ).df
                )
                bar.next()

        return pd.concat(objs=data, ignore_index=True)
