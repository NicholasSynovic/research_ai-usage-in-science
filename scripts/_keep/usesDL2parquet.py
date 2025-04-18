import re
from pathlib import Path

import click


def delete_text_between_words(paragraph, start_word, end_word):
    """
    Deletes text between two words in a paragraph using regular expressions.

    Args:
      paragraph: The input paragraph as a string.
      start_word: The word that marks the beginning of the text to delete.
      end_word: The word that marks the end of the text to delete.

    Returns:
      A string with the text between the start and end words removed.
      Returns the original paragraph if no matches are found.
    """

    pattern = re.escape(start_word) + r"(.*?)" + re.escape(end_word)
    matches = re.findall(pattern, paragraph, re.DOTALL)

    if not matches:
        return paragraph  # Return original if no match

    # Replace the matched text with an empty string
    new_paragraph = re.sub(pattern, "", paragraph, flags=re.DOTALL)
    return new_paragraph


@click.command()
@click.option(
    "-i",
    "--input",
    "inputFP",
    type=click.Path(
        exists=True,
        file_okay=True,
        readable=True,
        resolve_path=True,
        path_type=Path,
    ),
    required=True,
)
def main(inputFP: Path) -> None:
    content: str = open(file=inputFP, mode="r").read()

    print(
        delete_text_between_words(
            paragraph=content,
            start_word="<think>",
            end_word="</think>",
        )
    )


if __name__ == "__main__":
    main()
