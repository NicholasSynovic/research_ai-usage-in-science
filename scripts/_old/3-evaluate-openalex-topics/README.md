# Evaluate OpenAlex Topic Fields

> Download and analyze OpenAlex topic fields TODO: Finish this script

## Table Of Contents

- [Evaluate OpenAlex Topic Fields](#evaluate-openalex-topic-fields)
  - [Table Of Contents](#table-of-contents)
  - [About](#about)
  - [Program Logic](#program-logic)
  - [How To Run](#how-to-run)

## About

This directory contains the code and data necessary to evaluate OpenAlex topic
fields on different metrics including the number of domains, subfields, and
topics a particular field captures or is captured by.

## Program Logic

1. Get all OpenAlex topic API pages
1. Extract topics into a Pandas DataFrame
1. Extract subfields, domains, and fields into individual Pandas DataFrames
1. Join DataFrames into a single DataFrame
1. Print metrics of Natural Science fields

## How To Run
