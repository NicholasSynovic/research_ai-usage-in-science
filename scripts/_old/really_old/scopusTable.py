import pandas as pd
import requests
from bs4 import BeautifulSoup, Tag
from pandas import DataFrame


def parse_html(url: str) -> BeautifulSoup | None:
    """
    Fetches and parses an HTML page from the given URL.

    This function sends a GET request to the specified URL, and if the response
    status code is 200 (OK), it parses the HTML content using BeautifulSoup and
    returns the resulting BeautifulSoup object. If the status code is not 200,
    it prints an error message and returns None.

    :param url: The URL of the HTML page to be fetched and parsed.
    :type url: str
    :return: A BeautifulSoup object containing the parsed HTML, or None if the
             page could not be retrieved.
    :rtype: BeautifulSoup | None
    """  # noqa: E501
    response = requests.get(url, timeout=60)

    if response.status_code == 200:
        soup: BeautifulSoup = BeautifulSoup(
            markup=response.text,
            features="lxml",
        )
        return soup
    else:
        print(f"Failed to retrieve page: {response.status_code}")
        return None


def dataToDict(soup: BeautifulSoup) -> dict:
    """
    Extracts data from an HTML table and converts it into a dictionary.

    This function finds the first HTML table within the provided BeautifulSoup
    object, reads it into a Pandas DataFrame, selects specific columns, groups
    the data by the 'Subject area' column, and converts the grouped data into
    a dictionary.

    :param soup: A BeautifulSoup object containing the parsed HTML.
    :type soup: BeautifulSoup
    :return: A dictionary where the keys are 'Subject area' values and the values are lists of 'ASJC category' values.
    :rtype: dict
    """  # noqa: E501
    table: Tag = soup.find("table")
    df: DataFrame = pd.read_html(str(table))[0]

    df_selected = df[["ASJC category", "Subject area"]]

    return df_selected.groupby("Subject area")["ASJC category"].apply(list).to_dict()


def save_dict_to_file(dictionary: dict, filename: str) -> None:
    """
    Saves a dictionary to a file in a specific format.

    This function writes the given dictionary to a file in a format where each
    key-value pair is written as a list of strings. The output file will contain
    a Python dictionary definition with the given dictionary's contents.

    :param dictionary: The dictionary to be saved to a file.
    :type dictionary: dict
    :param filename: The name of the file where the dictionary will be saved.
    :type filename: str
    :return: None
    """  # noqa: E501
    with open(filename, "w") as file:
        file.write("SCOPUS_SUBJECTS: dict[str, List[str]] = {\n")
        for key, values in dictionary.items():
            file.write(f'\t"{key}": [\n')
            for value in values:
                file.write(f'\t\t"{value}",\n')
            file.write("\t],\n")
        file.write("}")


def main() -> None:
    """
    Main function to scrape data from a URL and save it to a file.

    This function performs the following steps:
    1. Fetches and parses an HTML page from a given URL.
    2. Extracts data from an HTML table and converts it into a dictionary.
    3. Saves the resulting dictionary to a file.

    :return: None
    """
    url: str = (
        "https://service.elsevier.com/app/answers/detail/a_id/15181/supporthub/scopus/"  # noqa: E501
    )
    soup: BeautifulSoup = parse_html(url)

    if soup:
        result_dict: dict = dataToDict(soup)
        save_dict_to_file(result_dict, "output.txt")


if __name__ == "__main__":
    main()
