from pathlib import Path
from typing import List
from urllib.parse import urlparse

import click
import pandas
import requests
from bs4 import BeautifulSoup
from progress.bar import Bar


def extractArtifact(URL: str) -> List[str]:
    try:
        response = requests.get(URL, timeout=20)
        response.raise_for_status()
        html_content = response.content

        soup = BeautifulSoup(html_content, "html.parser")

        article_info_div = soup.find("div", class_="articleinfo")

        if article_info_div:
            p_tags = article_info_div.find_all("p")

            if len(p_tags) >= 5:
                data_availability_p = p_tags[4]

                links = data_availability_p.find_all("a")
                if links:
                    hrefs = [
                        link["href"] for link in links if "href" in link.attrs
                    ]

                    return hrefs

        return []
    except requests.RequestException as e:
        print(f"Error fetching the page: {e}")
        return []


def getURLs(inputPath: str) -> List[List[str]]:
    df = pandas.read_parquet(inputPath)

    artifacts = []

    bar = Bar("Processing DOIs", max=len(df))
    for doi in df["doi"]:
        URL = doi

        artifactURLs: List[str] = extractArtifact(URL)

        if artifactURLs:
            artifacts.append(artifactURLs)
        bar.next()

    bar.finish()
    return artifacts


def extractDomains(urlLists: List[List[str]], outputPath: Path) -> List[str]:
    domains = []
    allURLs = []

    bar = Bar(
        "Extracting Domains", max=sum(len(urlList) for urlList in urlLists)
    )
    for urlList in urlLists:
        for url in urlList:
            try:
                parsed_url = urlparse(url)
                domain = parsed_url.netloc
                domains.append(domain)
                allURLs.append(url)
            except Exception as e:
                print(f"Error processing URL {url}: {e}")
                domains.append("N/A")
                allURLs.append(url)
            bar.next()

    bar.finish()

    domainsDf = pandas.DataFrame({"URL": allURLs, "Domain": domains})
    domainsDf.to_csv(outputPath, index=False)

    return domains


@click.command()
@click.option(
    "-i",
    "--input",
    "inputPath",
    type=click.Path(
        exists=True,
        file_okay=True,
        dir_okay=False,
        writable=False,
        readable=True,
        resolve_path=True,
        path_type=Path,
    ),
    required=True,
    help="Path to a transformed set of papers",
)
@click.option(
    "-o",
    "--output",
    "outputPath",
    type=click.Path(
        exists=True,
        file_okay=True,
        dir_okay=False,
        writable=False,
        readable=True,
        resolve_path=True,
        path_type=Path,
    ),
    required=True,
    help="Path to a csv file",
)
def main(inputPath: Path, outputPath: Path) -> None:
    artifacts = getURLs(inputPath)

    extractDomains(artifacts, outputPath)


if __name__ == "__main__":
    main()
