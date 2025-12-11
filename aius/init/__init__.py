"""
Initialize application runner variables.

Copyright 2025 (C) Nicholas M. Synovic

"""

from pandas import DataFrame

NATURAL_SCIENCE_OA_FIELDS: DataFrame = DataFrame(
    data={
        "field": [
            "Agricultural and Biological Sciences",
            "Biochemistry, Genetics and Molecular Biology",
            "Chemistry",
            "Earth and Planetary Sciences",
            "Environmental Science",
            "Immunology and Microbiology",
            "Neuroscience",
            "Physics and Astronomy",
        ],
        "openalex_id": [11, 13, 16, 19, 23, 24, 28, 31],
    }
)

JOURNAL_SEARCH_KEYWORDS: DataFrame = DataFrame(
    data={
        "keyword": [
            r'"Deep Learning"',
            r'"Deep Neural Network"',
            r'"Hugging Face"',
            r'"Model Checkpoint"',
            r'"Model Weights"',
            r'"Pre-Trained Model"',
        ]
    }
)


def compute_journal_search_years(
    min_year: int,
    max_year: int,
) -> DataFrame:
    years: list[int] = list(range(min_year, max_year + 1))
    return DataFrame(data={"year": years})
