# Download PLOS

> Download all of PLOS in Journal Publishing Tag Set (JATS) XML format

## Table Of Contents

- [Download PLOS](#download-plos)
  - [Table Of Contents](#table-of-contents)
  - [About](#about)
  - [Program Logic](#program-logic)
  - [How To Run](#how-to-run)

## About

This directory contains the code necessary to download every PLOS document in
JATS XML format. Only text is returned in this download. Figures are not
downloaded but are made availible via URIs in each document.

This script leverages the Unix `wget` application. If your system does not
support these applications, you can download the data from
[this URL](https://allof.plos.org/allofplos.zip).

## Program Logic

**NOTE:** If the file already exists on your system, then no data will be
downloaded.

1. Download the data to:

```shell
../../data/all_of_plos.zip
```

## How To Run

```shell
./download_plos.bash
```

or

```shell
wget \
  --no-clobber \
  -O ../../data/all_of_plos.zip  \
  https://allof.plos.org/allofplos.zip
```
