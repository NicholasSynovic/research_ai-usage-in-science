"""
LLM inference runner.

Copyright 2025 (C) Nicholas M. Synovic

"""

from difflib import SequenceMatcher
from itertools import islice
from json import JSONDecodeError, loads
from logging import Logger
from re import sub
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
        backend: Literal[
            "metis",
            "ollama",
            "openai",
            "openai-batch",
            "sophia",
        ] = "sophia",
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

    @staticmethod
    def _normalize_text(text: str) -> str:
        normalized: str = sub(pattern=r"[\s\W_]+", repl=" ", string=text)
        return normalized.lower().strip()

    @staticmethod
    def _heading_level(line: str) -> int | None:
        stripped: str = line.lstrip()
        if not stripped.startswith("#"):
            return None

        count: int = 0
        for character in stripped:
            if character != "#":
                break
            count += 1

        if count == 0 or count > 6:
            return None

        if len(stripped) <= count or stripped[count] != " ":
            return None

        return count

    @classmethod
    def _section_from_heading(
        cls,
        markdown_lines: list[str],
        heading_index: int,
    ) -> str:
        start_level: int | None = cls._heading_level(markdown_lines[heading_index])
        if start_level is None:
            return ""

        end_index: int = len(markdown_lines)
        for index in range(heading_index + 1, len(markdown_lines)):
            level: int | None = cls._heading_level(markdown_lines[index])
            if level is not None and level <= start_level:
                end_index = index
                break

        return "\n".join(markdown_lines[heading_index:end_index]).strip()

    @classmethod
    def _section_candidates(cls, markdown: str) -> list[str]:
        markdown_lines: list[str] = markdown.splitlines()
        candidates: list[str] = []

        for index, line in enumerate(markdown_lines):
            if cls._heading_level(line) is None:
                continue

            section: str = cls._section_from_heading(markdown_lines, index)
            if section:
                candidates.append(section)

        return candidates

    def _best_section_match(self, markdown: str, prose: str, doi: str) -> str:
        normalized_prose: str = self._normalize_text(prose)
        if not normalized_prose:
            self.logger.error("Empty prose for DOI %s", doi)
            return ""

        candidates: list[str] = self._section_candidates(markdown)

        for section in candidates:
            normalized_section: str = self._normalize_text(section)
            if normalized_prose in normalized_section:
                return section

        best_section: str = ""
        best_score: float = 0.0
        best_distance: int | None = None

        prose_tokens: set[str] = set(normalized_prose.split())
        if not prose_tokens:
            self.logger.error("Unable to tokenize prose for DOI %s: %s", doi, prose)
            return ""

        for section in candidates:
            normalized_section: str = self._normalize_text(section)
            score: float = SequenceMatcher(
                None,
                normalized_prose,
                normalized_section,
            ).ratio()
            if score < 0.8:
                continue

            distance: int = abs(len(normalized_section) - len(normalized_prose))
            if score > best_score or (
                score == best_score
                and (best_distance is None or distance < best_distance)
            ):
                best_section = section
                best_score = score
                best_distance = distance

        if best_section:
            return best_section

        self.logger.error(
            "Unable to match prose to a Markdown section for DOI %s: %s",
            doi,
            prose,
        )
        return ""

    def _parse_identify_ptms_response(self, response_text: str, doi: str) -> list[dict]:
        try:
            parsed_response: object = loads(response_text)
        except JSONDecodeError:
            self.logger.error("Unable to parse identify_ptms response for DOI %s", doi)
            return []

        if not isinstance(parsed_response, list):
            self.logger.error("identify_ptms response was not an array for DOI %s", doi)
            return []

        return [item for item in parsed_response if isinstance(item, dict)]

    def _expand_identify_ptms_documents(self, df: DataFrame) -> DataFrame:
        rows: list[dict[str, str]] = []

        for _, row in df.iterrows():
            doi: str = row["doi"]
            markdown: str = str(row["markdown"])

            for item in self._parse_identify_ptms_response(
                str(row["model_response"]), doi
            ):
                prose: str = str(item.get("prose", ""))
                if not prose.strip():
                    self.logger.error("Missing prose for DOI %s", doi)
                    continue

                section: str = self._best_section_match(
                    markdown=markdown, prose=prose, doi=doi
                )
                if not section:
                    continue

                rows.append({"doi": doi, "markdown": section})

        return DataFrame(rows)

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
                df = self.db.read_table_to_dataframe(
                    table_name="identify_ptms_analysis"
                )
                markdown_df: DataFrame = self.db.read_table_to_dataframe(
                    table_name="markdown"
                )
                df = df.merge(markdown_df[["doi", "markdown"]], on="doi", how="left")
                missing_markdown: int = int(df["markdown"].isna().sum())
                if missing_markdown:
                    self.logger.error(
                        "Missing markdown for %d identify_ptms row(s)",
                        missing_markdown,
                    )
                df = df.dropna(subset=["markdown"]).reset_index(drop=True)
            case "identify_ptm_reuse":
                df = self.db.read_table_to_dataframe(table_name="uses_ptms_analysis")
                df = self.__set_dataframe_formatting(df=df)
            case "identify_ptm_impact":
                df = self.db.read_table_to_dataframe(table_name="uses_ptms_analysis")
                df = self.__set_dataframe_formatting(df=df)

        if self.system_prompt_id == "identify_ptms":
            df = self._expand_identify_ptms_documents(df=df)
        else:
            if "markdown" not in df.columns:
                df = df.rename(columns={"user_prompt": "markdown"})

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

        if self.backend.name != "openaibatch":
            df.to_parquet(
                path=f"aius_{self.backend.name}_{self.system_prompt_id}_index-{self.index}_stride-{self.stride}.parquet",
                engine="auto",
            )

        return 0
