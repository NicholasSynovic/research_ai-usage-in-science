"""
Global variables for `aius`.

Copyright 2025 (C) Nicholas M. Synovic

"""

from mdformat import text
from pandas import DataFrame

MODULE_NAME: str = "aius"
PROGRAM_NAME: str = "AIUS"
PROGRAM_DESCRIPTION: str = "Identify AI usage in Natural Science research papers"
PROGRAM_EPILOG: str = "Copyright 2025 (C) Nicholas M. Synovic"
JOURNALS: DataFrame = DataFrame(data={"journal": ["Nature", "PLOS", "Science"]})
GET_TIMEOUT: int = 60
POST_TIMEOUT: int = 36000
YEAR_LIST: list[int] = list(range(2014, 2025))
YEARS: DataFrame = DataFrame(data={"year": YEAR_LIST})

FIELD_FILTER: set[str] = {
    "Agricultural and Biological Sciences",
    "Environmental Science",
    "Biochemistry, Genetics and Molecular Biology",
    "Immunology and Microbiology",
    "Neuroscience",
    "Earth and Planetary Sciences",
    "Physics and Astronomy",
    "Chemistry",
}

KEYWORD_LIST: list[str] = [
    r'"Deep Learning"',
    r'"Deep Neural Network"',
    r'"Hugging Face"',
    r'"HuggingFace"',
    r'"Model Checkpoint"',
    r'"Model Weights"',
    r'"Pre-Trained Model"',
]


SEARCH_KEYWORDS: DataFrame = DataFrame(
    data={
        "keyword": [
            r'"Deep Learning"',
            r'"Deep Neural Network"',
            r'"Hugging Face"',
            r'"HuggingFace"',
            r'"Model Checkpoint"',
            r'"Model Weights"',
            r'"Pre-Trained Model"',
        ]
    }
)

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
