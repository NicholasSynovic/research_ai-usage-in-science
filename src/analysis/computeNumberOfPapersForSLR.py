import click

NUMBER_OF_PAPERS_PER_YEAR: int = 10


@click.command()
@click.option(
    "-s",
    "--start-year",
    "startYear",
    help="First year of the analysis",
    default=2014,
    required=False,
    show_default=True,
)
@click.option(
    "-e",
    "--end-year",
    "endYear",
    help="Last year of the analysis",
    default=2024,
    required=False,
    show_default=True,
)
@click.option(
    "-n",
    "--number-of-papers",
    "numberOfPapers",
    type=int,
    help="Number of papers per year",
    default=10,
    required=False,
    show_default=True,
)
def main(startYear: int, endYear: int, numberOfPapers: int) -> None:
    print("Starting Year:", startYear)
    print("Ending Year:", endYear)
    print("Number Of Papers Per Year:", numberOfPapers)

    yearDifference: int = endYear - startYear + 1
    print(f"Year Difference [{startYear} - {endYear}]:", yearDifference)

    print("Total Papers To Read:", yearDifference * numberOfPapers)


if __name__ == "__main__":
    main()
