from pandas import DataFrame, Series

from src.db import DB


def countTotalSearchResultsFromPLOS(db: DB) -> int:
    """
    Total search results from PLOS
    """
    df: DataFrame = db.getPLOSPapersPerKeyword()
    data: int = df["keyword"].count()
    return data


def countTotalUniqueSearchResultsFromPLOS(db: DB) -> int:
    """
    Total unique search results from PLOS
    The first entry is always kept
    """
    df: DataFrame = db.getPLOSPapersPerKeyword()
    df.drop_duplicates(subset="document_id", keep="first", inplace=True)
    data: int = df["keyword"].count()
    return data


def countTotalCompletelyUniqueSearchResultsFromPLOS(db: DB) -> int:
    """
    Total completely unique search results from PLOS
    No duplicates are kept
    """
    df: DataFrame = db.getPLOSPapersPerKeyword()
    df.drop_duplicates(subset="document_id", keep=False, inplace=True)
    data: int = df["keyword"].count()
    return data


def countTotalSearchResultsFromPLOSByKeyword(db: DB) -> Series:
    """
    Total search results from PLOS by keyword
    """
    df: DataFrame = db.getPLOSPapersPerKeyword()
    data: Series = df["keyword"].value_counts()
    return data


def countTotalUniqueSearchResultsFromPLOSByKeyword(db: DB) -> Series:
    """
    Total unique search results from PLOS by keyword
    The first entry is always kept
    """
    df: DataFrame = db.getPLOSPapersPerKeyword()
    df.drop_duplicates(subset="document_id", keep="first", inplace=True)
    data: Series = df["keyword"].value_counts()
    return data


def countTotalCompletelyUniqueSearchResultsFromPLOSByKeyword(db: DB) -> Series:
    """
    Total unique search results from PLOS by keyword
    The first entry is always kept
    """
    df: DataFrame = db.getPLOSPapersPerKeyword()
    df.drop_duplicates(subset="document_id", keep=False, inplace=True)
    data: Series = df["keyword"].value_counts()
    return data
