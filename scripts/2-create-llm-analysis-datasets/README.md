# Create Prompt Testing Datasets

> Create datasets to evaluate potential system prompts

## Table Of Contents

- [Create Prompt Testing Datasets](#create-prompt-testing-datasets)
  - [Table Of Contents](#table-of-contents)
  - [About](#about)
  - [Program Logic](#program-logic)
  - [How To Run](#how-to-run)

## About

This directory contains the code and data necessary to evaluate different system
prompts during the LLM analysis. These datasets conform to the same input as the
LLM analysis framework, but have fewer data points to evaluate.

This script leverages the Unix `pandoc` application.

## Program Logic

1. Load zip archive containing PLOS documents in JATS XML format
1. For each unique DOI in the dataset, load the JATS XML format
1. Store the raw JATS XML content
1. Store JATS XML content without the front matter and citations
1. Convert the raw JATS XML content into Markdown and store it
1. Conver the formatted JATS XML content into Markdown and store it
1. For each document per format, compute the token count and store it in columns

## How To Run

In a terminal, run:

```shell
pandoc server
```

In a seperate terminal, run:

```shell
python create_prompt_testing_dataset.py --help
Usage: create_prompt_testing_dataset.py [OPTIONS]

Options:
  -i, --input-fp <LAMBDA>         Path to PLOS JATS XML archive  [required]
  -d, --dataset-size [small|manual-review]
                                  Dataset size  [default: small]
  -o, --output-fp <LAMBDA>        Path to store dataset as an Apache Parquet
                                  File  [default:
                                  prompt_testing_dataset.parquet]
  --help                          Show this message and exit.
```
