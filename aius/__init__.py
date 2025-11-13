"""
Global variables for `aius`.

Copyright 2025 (C) Nicholas M. Synovic

"""

from pandas import DataFrame

MODULE_NAME: str = "aius"
PROGRAM_NAME: str = "AIUS"
PROGRAM_DESCRIPTION: str = "Identify AI usage in Natural Science research papers"
PROGRAM_EPILOG: str = "Copyright 2025 (C) Nicholas M. Synovic"
GET_TIMEOUT: int = 60
POST_TIMEOUT: int = 36000

LLM_PROMPT_ENGINEERING_PAPERS: DataFrame = DataFrame(
    data={
        "doi": [
            "https://doi.org/10.1371/journal.pcbi.1010512",
            "https://doi.org/10.1371/journal.pcbi.1011818",
            "https://doi.org/10.1371/journal.pdig.0000536",
            "https://doi.org/10.1371/journal.pgen.1009436",
            "https://doi.org/10.1371/journal.pntd.0010937",
            "https://doi.org/10.1371/journal.pone.0086152",
            "https://doi.org/10.1371/journal.pone.0088597",
            "https://doi.org/10.1371/journal.pone.0093666",
            "https://doi.org/10.1371/journal.pone.0095718",
            "https://doi.org/10.1371/journal.pone.0096811",
            "https://doi.org/10.1371/journal.pone.0101765",
            "https://doi.org/10.1371/journal.pone.0103831",
            "https://doi.org/10.1371/journal.pone.0113159",
            "https://doi.org/10.1371/journal.pone.0114812",
            "https://doi.org/10.1371/journal.pone.0120570",
            "https://doi.org/10.1371/journal.pone.0185844",
            "https://doi.org/10.1371/journal.pone.0192011",
            "https://doi.org/10.1371/journal.pone.0196302",
            "https://doi.org/10.1371/journal.pone.0209649",
            "https://doi.org/10.1371/journal.pone.0217305",
        ]
    }
)
