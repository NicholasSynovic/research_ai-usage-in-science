# Research Steps

## Table Of Contents

- [Research Steps](#research-steps)
  - [Table Of Contents](#table-of-contents)
  - [About](#about)
  - [Pilot Study](#pilot-study)

## About

We are interested in studying how computational natural scientists (CNS) reuse
pre-trained deep learning models (PTMs) in their research. To study this, we
need to analyze the peer-reviewed, published works of CNS. We can contextualize
this difference between CNS and traditional software engineers (TSE) by
reviewing the SE methods/ processes of CNS that have already been identified

## Pilot Study

The data that we want to analyze for this study is the peer-reviewed, published
works of CNS. Rather than searching for all journals through OpenAlex, World of
Science, or Scopus for documents, we will narrow our search to the following
publishers:

- Nature [https://www.nature.com/](https://www.nature.com/)
- Science [https://www.science.org/](https://www.science.org/)
- PLOS [https://journals.plos.org/plosone](https://journals.plos.org/plosone)

These journals were identified based on the reccomendations from advisors and
colleagues of the authors.

To search these journals for the pilot study, we will perform a *manual* search
of each publisher. We will save the results of these searches as `.html` files
and will not include the text content of paper results at this time. To search a
publisher, we will use their provided search bars and only filter on search
queries.

The following search queries are to be used:

- "Deep Learning"
- "Deep Neural Network"
- "Hugging Face"
- "Pre-Trained Model"
- "Model Weights"
- "Model Checkpoints"

**NOTE**: The double quotes must be wrapped around each search query.

This data will be availible in
`./data/0_pilot_study/{journal}/{search_query}/{page_number}.html`
