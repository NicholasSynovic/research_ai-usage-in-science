# An Exploratory Mixed-Methods Study of Deep Neural Network Reuse in Computational Natural Science

> Submitted to
> [ESEM'25 - Technical Track](https://conf.researchr.org/track/esem-2025/esem-2025-technical-track)
> TODO: Update authors after double blind review TODO: Add link to the pre-print
> article TODO: Add link to data hosted on Zenodo

This repository contains the source code used for *An Exploratory Mixed-Methods
Study of Deep Neural Network Reuse in Computational Natural Science*. If you are
looking for the data used in the study, we have released our SQLite3 database
and author agreement excel workbooks to Zenodo.

## Table Of Contents

- [An Exploratory Mixed-Methods Study of Deep Neural Network Reuse in Computational Natural Science](#an-exploratory-mixed-methods-study-of-deep-neural-network-reuse-in-computational-natural-science)
  - [Table Of Contents](#table-of-contents)
  - [About](#about)
    - [Open-Access Data Collection](#open-access-data-collection)
  - [OpenAlex](#openalex)
  - [Automated Analysis With Ollama Models](#automated-analysis-with-ollama-models)
  - [Dependencies](#dependencies)
  - [How To Install](#how-to-install)
  - [How To Run](#how-to-run)
  - [Tutorial](#tutorial)

## About

> TODO: Add links to each tutorial section TODO: Release template Excel (.xslx)
> file for author agreement with instructions on how to use it

This repository contains the source code to automatically search and filter for
Natural Science publications from Nature and PLOS using OpenAlex. It also
includes all of our code to capture and parse the metadata, as well as bulk
download open-access articles from Nature and PLOS. Finally, it also includes
the code to run an automated analysis of our study on arbiturary papers using
pre-trained foundational reasoning and non-reasoning large language models
(LLMs) via Ollama. We have provided a runner script to execute all autonomous
operations and figure generations of our work. For the manual review portions of
study, we have released a template Excel (.xlsx) workbook and instructions on
how to perform our author agreement process.

### Open-Access Data Collection

> TODO: Release PDFs as part of the Zenodo artifact

Our work is based on peer-reviewed, open-access academic articles from PLOS and
Nature. As part of our Zenodo artifact, we have released the `.pdf` documents
leveraged in our study from both PLOS and Nature. While it may be possible to
leverage our methods on non-open-access works, we make no claims to its
effectiveness our efficacy.

> TODO: Review TOS to ensure that this is accurate

At the time of this study, both PLOS's and Nature's Terms Of Service (TOS)
supported the collection, aggregation, and release of open-access works in
scientific pursuit. Prior to bulk downloading any documents from Nature or PLOS,
we advise the reader to review both
[Nature's TOS](https://www.nature.com/info/terms-and-conditions) and
[PLOS's TOS](https://plos.org/terms-of-use/).

## OpenAlex

OpenAlex is an open database of scientific works and their metadata. We leverage
OpenAlex extensively to extract academic work metadata in a journal agnostic
manner. Additionally, we rely on OpenAlex's topic identification system to
filter for Natural Science (i.e., Chemistry, Biology, Physics, and Environmental
Science). You can read more about this system
[here](https://docs.openalex.org/api-entities/topics).

In our Zenodo release, we store the OpenAlex responses within the SQLite3
artifact in the `openalex_responses` table. As OpenAlex continously updates its
aggregated works, we recommend reproducers of our work to leverage the stored
responses.

## Automated Analysis With Ollama Models

Leveraging the results from the author agreement process described in our paper,
we leveraged pre-trained foundational reasoning and non-reasoning models to
automatically review the bulk of remaining papers

## Dependencies

asdf

## How To Install

```shell
make create-dev
source env/bin/activate
make build
make package
```

## How To Run

We have created a pipeline that you can execute to reproduce the work. Please
run `./run.bash {{EMAIL_ADDRESS}}` where `{{EMAIL_ADDRESS}}` is a valid email to
access the
[OpenAlex API polite pool](https://docs.openalex.org/how-to-use-the-api/rate-limits-and-authentication#the-polite-pool).

## Tutorial

asdf
