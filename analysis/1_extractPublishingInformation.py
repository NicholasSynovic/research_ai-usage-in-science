from collections import defaultdict
from os import listdir
from pathlib import Path
from typing import List

import click
from bs4 import BeautifulSoup, Tag
from pandas import DataFrame

RESULTS: defaultdict = defaultdict(int)
RESULTS["Deep Learning"]
RESULTS["Deep Neural Network"]
RESULTS["Hugging Face"]
RESULTS["HuggingFace"]
RESULTS["Model Checkpoints"]
RESULTS["Model Weights"]
RESULTS["Pre-Trained Model"]
RESULTS["Total"]

def identifyFilepaths(dir: Path)    ->  List[Path]:
    data: List[Path] = []
    parentDir: List[Path] = [Path(dir, fp) for fp in listdir(path=dir)]

    foo: Path
    for foo in parentDir:
        data.extend([Path(foo, fp) for fp in listdir(path=foo)])

    return data

def extractNature(fps: List[Path])  ->  dict[str, int]:
    fp: Path
    for fp in fps:
        soup: BeautifulSoup = BeautifulSoup(markup=open(fp), features="lxml")
        title: str = soup.find(name="title").text.split("|")[0].strip().replace('"', "")
        resultCount: int = soup.find(name="span", attrs={"class": "u-display-flex",}).

        print(title, container.text)



@click.command()
@click.option(
    "-i",
    "--input",
    "inputDirectory",
    required=True,
    help="Path to a directory to analyze search results from the refined study.",
    type=click.Path(exists=True, dir_okay=True, readable=True, resolve_path=True, path_type=Path,)
)
@click.option(
    "-p",
    "--publisher",
    "publisher",
    required=True,
    help="Search result publisher",
    type=click.Choice(choices=["nature", "plos", "science"], case_sensitive=True,)
)
def main(inputDirectory: Path, publisher: str)  ->  None:
    fps: List[Path] = identifyFilepaths(dir=inputDirectory)
    extractNature(fps=fps)



if __name__ == "__main__":
    main()
