from aius.analyze.prompts import *

SYSTEM_PROMPT_TAG_MAPPING: dict[str, COSTAR_SystemPrompt] = {
    "uses_dl": USES_DL_PROMPT,
    "uses_ptms": USES_PTMS_PROMPT,
    "identify_ptms": IDENTIFY_PTMS_PROMPT,
    "identify_ptm_reuse": IDENTIFY_PTM_REUSE_PROMPT,
    "identify_ptm_impact": IDENTIFY_PTM_IMPACT_IN_SCIENTIFIC_PROCESS,
}
