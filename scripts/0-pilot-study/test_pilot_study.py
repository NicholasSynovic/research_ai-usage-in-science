import pilot_study as ps
from pandas import DataFrame
from requests import Response


def test_create_urls() -> None:
    urls: list[str] = ps.create_urls()  # Get the output of the code

    assert isinstance(urls, list)
    assert len(urls) == 77
    assert len(set(urls)) == 77


def test_get_all_pages() -> None:
    GAP_DF: DataFrame = ps.get_all_pages(urls=ps.create_urls())

    assert isinstance(GAP_DF, DataFrame)
    assert GAP_DF.shape == (77, 3)
    assert GAP_DF.columns.to_list() == ["url", "response", "json"]

    resp: Response
    for resp in GAP_DF["response"]:
        assert resp.status_code == 200


def test_get_document_ids() -> None:
    document_ids: set = ps.get_document_ids(df=ps.get_all_pages(urls=ps.create_urls()))

    assert isinstance(document_ids, set)
    assert len(document_ids) == 53
