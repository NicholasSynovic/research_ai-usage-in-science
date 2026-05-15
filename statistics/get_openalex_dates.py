from sqlite3 import Connection, connect

import pandas
from pandas import DataFrame, Timestamp

FIELD: list[str] = [
    "Agricultural and Biological Sciences",
    "Biochemistry, Genetics and Molecular Biology",
    "Chemistry",
    "Earth and Planetary Sciences",
    "Environmental Science",
    "Immunology and Microbiology",
    "Neuroscience",
    "Physics and Astronomy",
]


def load_data(conn: Connection) -> DataFrame:
    sql: str = """
SELECT
    doi,
    json_extract(json_data, '$.publication_date') AS publication_date,
    topic_0,
    topic_1,
    topic_2
FROM
    openalex;
"""
    return pandas.read_sql_query(sql=sql, con=conn)


def get_dois_published_in_year(df: DataFrame, year: int = 2024) -> DataFrame:
    return df[
        (df["publication_date"] >= Timestamp(ts_input=f"{year}-01-01"))
        & (df["publication_date"] < Timestamp(ts_input=f"{year + 1}-01-01"))
    ]


def get_ns_dois_published_in_year(df: DataFrame, year: int = 2024) -> DataFrame:
    return df[
        (
            (df["publication_date"] >= Timestamp(ts_input=f"{year}-01-01"))
            & (df["publication_date"] < Timestamp(ts_input=f"{year + 1}-01-01"))
        )
        & (
            df["topic_0"].isin(FIELD)
            | df["topic_1"].isin(FIELD)
            | df["topic_2"].isin(FIELD)
        )
    ]


def main() -> None:
    conn: Connection = connect(database="../data/aius.3-18-2026.db")
    df: DataFrame = load_data(conn=conn)

    df["publication_date"] = df["publication_date"].apply(Timestamp)
    df = df.sort_values(by="publication_date", ascending=False)

    print(
        2024,
        get_dois_published_in_year(df=df, year=2024).shape,
        get_ns_dois_published_in_year(df=df, year=2024).shape,
    )
    print(
        2025,
        get_dois_published_in_year(df=df, year=2025).shape,
        get_ns_dois_published_in_year(df=df, year=2025).shape,
    )


if __name__ == "__main__":
    main()
