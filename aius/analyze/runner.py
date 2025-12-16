"""
LLM inference runner.

Copyright 2025 (C) Nicholas M. Synovic

"""

from itertools import islice
from json import loads
from logging import Logger
from typing import Literal

import pandas as pd
from pandas import DataFrame

from aius.analyze import BACKEND_MAPPING
from aius.analyze.backend import Backend
from aius.analyze.data_models import Document, ModelResponse
from aius.db import DB
from aius.runner import Runner


class AnalysisRunner(Runner):  # noqa: D101
    def __init__(  # noqa: D107, PLR0917, PLR0913
        self,
        db: DB,
        logger: Logger,
        index: int,
        model_name: str,
        stride: int,
        system_prompt_id: str,
        auth_key: str = "",
        backend: Literal["metis", "ollama", "sophia"] = "sophia",
        max_context_tokens: int = 100000,
        max_predict_tokens: int = 10000,
        ollama_endpoint: str = "",
    ) -> None:
        super().__init__(name="analysis", db=db, logger=logger)

        self.stride: int = stride
        self.index: int = index
        self.ollama_endpoint: str = ollama_endpoint
        self.system_prompt_id: str = system_prompt_id.lower()

        self.backend: Backend = BACKEND_MAPPING[backend](
            name=backend,
            logger=self.logger,
            model_name=model_name,
            auth_key=auth_key,
            ollama_endpoint=ollama_endpoint,
            max_context_tokens=max_context_tokens,
            max_predict_tokens=max_predict_tokens,
        )

        self.system_prompt: str = self._get_system_prompt()

    def _get_system_prompt(self) -> str:
        return self.db.get_llm_prompt(llm_prompt_id=self.system_prompt_id)

    def __set_dataframe_formatting(self, df: DataFrame) -> DataFrame:
        df["model_response"] = df["model_response"].replace(
            to_replace="",
            value=float("NaN"),
            inplace=False,
        )
        df = df.dropna(inplace=False, ignore_index=True)
        df["model_response"] = df["model_response"].apply(loads)
        df = df[df["model_response"].apply(lambda d: d.get("result") is True)]
        df.reset_index(drop=True, inplace=True)
        df.rename(columns={"user_prompt": "markdown"}, inplace=True)
        return df

    def _get_documents(self) -> list[Document]:
        df: DataFrame = DataFrame()

        match self.system_prompt_id:
            case "uses_dl":
                df = self.db.read_table_to_dataframe(table_name="markdown")
            case "uses_ptms":
                df = self.db.read_table_to_dataframe(table_name="uses_dl_analysis")
                df = self.__set_dataframe_formatting(df=df)
            case "identify_ptms":
                df = self.db.read_table_to_dataframe(table_name="uses_ptms_analysis")
                df = self.__set_dataframe_formatting(df=df)
            case "identify_ptm_reuse":
                df = self.db.read_table_to_dataframe(table_name="uses_ptms_analysis")
                df = self.__set_dataframe_formatting(df=df)
            case "identify_ptm_impact":
                df = self.db.read_table_to_dataframe(table_name="uses_ptms_analysis")
                df = self.__set_dataframe_formatting(df=df)

        df_islice: islice = islice(
            df.iterrows(),
            self.index,
            None,
            self.stride,
        )

        return [
            Document(doi=row["doi"], content=row["markdown"]) for _, row in df_islice
        ]

    def execute(self) -> int:  # noqa: D102
        documents: list[Document] = self._get_documents()

        responses: list[ModelResponse] = self.backend.inference_documents(
            documents=documents,
            system_prompt=self.system_prompt,
        )

        df: DataFrame = pd.concat(
            objs=[resp.to_df for resp in responses],
            ignore_index=True,
        )

        df.to_parquet(
            path=f"aius_{self.backend.name}_{self.system_prompt_id}_index-{self.index}_stride-{self.stride}.parquet",
            engine="auto",
        )

        return 0
