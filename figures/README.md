# Guide To Understanding Figure Order

## Table of Contents

- [Guide To Understanding Figure Order](#guide-to-understanding-figure-order)
  - [Table of Contents](#table-of-contents)
  - [0. Total Nature and PLOS Papers](#0-total-nature-and-plos-papers)
  - [1. Total Nature and PLOS Natural Science Papers](#1-total-nature-and-plos-natural-science-papers)
  - [2. Frequency of Top-5 Primary Topics From Nature and PLOS](#2-frequency-of-top-5-primary-topics-from-nature-and-plos)
  - [3. Frequency of Natural Science Topics From Nature and PLOS](#3-frequency-of-natural-science-topics-from-nature-and-plos)
  - [4. Number of Papers Published in PLOS and Nature per Year](#4-number-of-papers-published-in-plos-and-nature-per-year)
  - [5. Number of Natural science Papers Published in PLOS and Nature per Year](#5-number-of-natural-science-papers-published-in-plos-and-nature-per-year)
  - [Breakdown Of PLOS Keyword Searches](#breakdown-of-plos-keyword-searches)

## 0. Total Nature and PLOS Papers

This figure displays a bar chart of the total number of Nature and PLOS papers
captured in our search.

- [Code](total_plos_nature_papers.py)
- [Figure](total_plos_nature_papers.pdf)

## 1. Total Nature and PLOS Natural Science Papers

This figure displays a bar chart of the total number of Nature and PLOS *natural
science* papers captured in our search. Natural science papers are identified by
having at least one citation and two topics that are were identified as being
relevant to Natural Science. Citation counts and topics are provided via
OpenAlex.

- [Code](total_plos_nature_natural_science_papers.py)
- [Figure](total_plos_nature_natural_science_papers.pdf)

## 2. Frequency of Top-5 Primary Topics From Nature and PLOS

This figure displays a bar chart where the X-Axis is of the top-5 OpenAlex
primary topic (the first topic), and the Y-Axis is the frequency of that topic.
Each topic has two associated bars, one red and one blue. The red bar represents
the topics captured from Nature, the blue represents topics from PLOS. This does
not filter for natural science specific primary topics and considers all primary
topics.

- [Code](frequency_of_top_5_primary_topics_nature_plos.py)
- [Figure](frequency_of_top_5_primary_topics_nature_plos.pdf)

## 3. Frequency of Natural Science Topics From Nature and PLOS

This figure displays a bar chart where the X-Axis is of the OpenAlex natural
science topics, and the Y-Axis is the frequency of that topic. Each topic has
two associated bars, one red and one blue. The red bar represents the topics
captured from Nature, the blue represents topics from PLOS. As each paper can
have three topics, the frequency of topics will be greater than the number of
papers.

- [Code](frequency_of_natural_science_topics.py)
- [Figure](frequency_of_natural_science_topics.pdf)

## 4. Number of Papers Published in PLOS and Nature per Year

This figure's X Axis is the year, and the Y axis is the number of papers
published. There are two bars per x tick. One for Nature and another for PLOS.

- [Code](number_of_papers_published_per_year.py)
- [Figure](number_of_papers_published_per_year.pdf)

## 5. Number of Natural science Papers Published in PLOS and Nature per Year

This figure's X Axis is the year, and the Y axis is the number of natural
science papers published. There are two bars per x tick. One for Nature and
another for PLOS.

- [Code](number_of_natural_science_papers_published_per_year.py)
- [Figure](number_of_natural_science_papers_published_per_year.pdf)

## Breakdown Of PLOS Keyword Searches

This generates a table of the following columns for PLOS search results:

- Keyword: The keyword used in the search
- Total Documents: The total number of documents returned in the search
- Unique Documents: The total number of *unique* documents returned in the
  search

It also reports the total number of documents returned across all searches, and
the total number of unique documents returned.

- [Code](breakdown_of_plos_keyword_searches.py)
- [Figure](breakdown_of_plos_keyword_searches.py)
