"""
Global variables for `aius`.

Copyright 2025 (C) Nicholas M. Synovic

"""

from pandas import DataFrame

MODULE_NAME: str = "aius"
PROGRAM_NAME: str = "AIUS"
PROGRAM_DESCRIPTION: str = "Identify AI usage in Natural Science research papers"
PROGRAM_EPILOG: str = "Copyright 2025 (C) Nicholas M. Synovic"

FIELD_FILTER: set[str] = {
    "Agricultural and Biological Sciences",
    "Environmental Science",
    "Biochemistry Genetics and Molecular Biology",
    "Immunology and Microbiology",
    "Neuroscience",
    "Earth and Planetary Sciences",
    "Physics and Astronomy",
    "Chemistry",
}


GET_TIMEOUT: int = 60
POST_TIMEOUT: int = 60

KEYWORD_LIST: list[str] = [
    r'"Deep Learning"',
    r'"Deep Neural Network"',
    r'"Hugging Face"',
    r'"HuggingFace"',
    r'"Model Checkpoint"',
    r'"Model Weights"',
    r'"Pre-Trained Model"',
]
YEAR_LIST: list[int] = list(range(2014, 2025))

YEARS: DataFrame = DataFrame(data={"year": list(range(2014, 2025))})

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

JOURNALS: DataFrame = DataFrame(data={"journal": ["Nature", "PLOS", "Science"]})
