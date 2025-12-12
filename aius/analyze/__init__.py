"""
System prompts and models for analyzing documents.

Copyright 2025 (C) Nicholas M. Synovic

"""

from pandas import DataFrame

from aius.analyze.data_models import (
    IDENTIFY_PTM_IMPACT_IN_SCIENTIFIC_PROCESS,
    IDENTIFY_PTM_REUSE_PROMPT,
    IDENTIFY_PTMS_PROMPT,
    USES_DL_PROMPT,
    USES_PTMS_PROMPT,
    COSTAR_SystemPrompt,
)
from aius.analyze.metis import Metis
from aius.analyze.ollama import Ollama
from aius.analyze.sophia import Sophia

BACKEND_MAPPING: dict[str, type] = {
    "metis": Metis,
    "ollama": Ollama,
    "sophia": Sophia,
}

SYSTEM_PROMPT_TAG_MAPPING: dict[str, COSTAR_SystemPrompt] = {
    "uses_dl": USES_DL_PROMPT,
    "uses_ptms": USES_PTMS_PROMPT,
    "identify_ptms": IDENTIFY_PTMS_PROMPT,
    "identify_ptm_reuse": IDENTIFY_PTM_REUSE_PROMPT,
    "identify_ptm_impact": IDENTIFY_PTM_IMPACT_IN_SCIENTIFIC_PROCESS,
}

SYSTEM_PROMPT_TAG_MAPPING_DF: DataFrame = DataFrame(
    data={
        "tag": [p.tag for p in SYSTEM_PROMPT_TAG_MAPPING.values()],
        "prompt": [p.create_prompt() for p in SYSTEM_PROMPT_TAG_MAPPING.values()],
        "json_string": [
            p.model_dump_json(indent=4) for p in SYSTEM_PROMPT_TAG_MAPPING.values()
        ],
    }
)
