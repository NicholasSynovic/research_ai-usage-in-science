# Pilot Study

> Return a set of the most cited documents per search query per year

## Table Of Contents

- [Pilot Study](#pilot-study)
  - [Table Of Contents](#table-of-contents)
  - [About](#about)
  - [Program Logic](#program-logic)
  - [Program Output](#program-output)
  - [How To Run](#how-to-run)
  - [How To Test](#how-to-test)

## About

This directory contains the data and code necessary to return a unique set of
PLOS hosted document DOIs per search query per year. These DOIs are found by
querying PLOS for each search query per year, and then sorting by citation
count, and filtering for only the most cited document per search query.

## Program Logic

**NOTE:** If a file that matches the `--output` argument already exists, that
file will be read into the application and steps 1 - 4 will be skipped.

1. Construct a list of all search query + year URL combinations.
1. Query each URL.
1. Store the URL, Response, and relevant JSON objects into a Pandas DataFrame
1. Write the data to an Python Pickle file at the `--output` location
1. Get the unique set of PLOS document DOIs
1. Print the unique set of PLOS document DOIs to the terminal

## Program Output

In the event of data loss or corruption, the following PLOS Document DOIs were
printed to Nicholas M. Synovic's personal laptop on October 6th, 2025:

```text
10.1371/journal.pstr.0000051
10.1371/journal.ppat.1007410
10.1371/journal.pone.0304868
10.1371/journal.pone.0304013
10.1371/journal.pone.0300919
10.1371/journal.pone.0297958
10.1371/journal.pone.0295951
10.1371/journal.pone.0290691
10.1371/journal.pone.0289795
10.1371/journal.pone.0281815
10.1371/journal.pone.0270904
10.1371/journal.pone.0262838
10.1371/journal.pone.0254841
10.1371/journal.pone.0251415
10.1371/journal.pone.0250952
10.1371/journal.pone.0242301
10.1371/journal.pone.0237861
10.1371/journal.pone.0235187
10.1371/journal.pone.0233678
10.1371/journal.pone.0232391
10.1371/journal.pone.0229963
10.1371/journal.pone.0225385
10.1371/journal.pone.0223994
10.1371/journal.pone.0212550
10.1371/journal.pone.0207982
10.1371/journal.pone.0197704
10.1371/journal.pone.0174944
10.1371/journal.pone.0172578
10.1371/journal.pone.0169748
10.1371/journal.pone.0158765
10.1371/journal.pone.0156327
10.1371/journal.pone.0155781
10.1371/journal.pone.0144610
10.1371/journal.pone.0141287
10.1371/journal.pone.0130140
10.1371/journal.pmed.1002730
10.1371/journal.pmed.1002686
10.1371/journal.pmed.1001757
10.1371/journal.pgen.1010105
10.1371/journal.pgen.1007889
10.1371/journal.pdig.0000341
10.1371/journal.pdig.0000198
10.1371/journal.pdig.0000022
10.1371/journal.pdig.0000016
10.1371/journal.pcbi.1011462
10.1371/journal.pcbi.1008736
10.1371/journal.pcbi.1008724
10.1371/journal.pcbi.1006633
10.1371/journal.pcbi.1005324
10.1371/journal.pcbi.1003915
10.1371/journal.pcbi.1003889
10.1371/journal.pbio.3002366
10.1371/journal.pbio.1002073
```

## How To Run

```shell
python pilot_study.py --help

Usage: pilot_study.py [OPTIONS]

Options:
  -o, --output <LAMBDA>  Path to store output Python Pickle file  [default: ./pilot_study.pickle]
  --help                 Show this message and exit.
```

## How To Test

Tests are written using `pytest`

```shell
pytest test_pilot_study.py
```
