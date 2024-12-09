# Research Steps

## Table Of Contents

- [Research Steps](#research-steps)
  - [Table Of Contents](#table-of-contents)
  - [About](#about)
  - [Initial Study](#initial-study)
    - [Results](#results)
  - [Refined Study](#refined-study)

## About

We are interested in studying how computational natural scientists (CNS) reuse
pre-trained deep learning models (PTMs) in their research. To study this, we
need to analyze the peer-reviewed, published works of CNS. We can contextualize
this difference between CNS and traditional software engineers (TSE) by
reviewing the SE methods/ processes of CNS that have already been identified

## Initial Study

The data that we want to analyze for this study is the peer-reviewed, published
works of CNS. Rather than searching for all journals through OpenAlex, World of
Science, or Scopus for documents, we will narrow our search to the following
publishers:

- Nature [https://www.nature.com/](https://www.nature.com/)
- Science [https://www.science.org/](https://www.science.org/)
- PLOS
  [https://journals.plos.org/plosone/dynamicSearch?filterJournals=PLoSONE&q=](https://journals.plos.org/plosone/dynamicSearch?filterJournals=PLoSONE&q=)

These journals were identified based on the reccomendations from advisors and
colleagues of the authors.

To search these journals for the pilot study, we will perform a *manual* search
of each publisher. We will save the results of these searches as `.html` or
`.json` files and will not include the text content of paper results at this
time. To search a publisher, we will use their provided search bars and only
filter on search queries.

The following search queries are to be used:

- "Deep Learning"
- "Deep Neural Network"
- "Hugging Face"
- "Pre-Trained Model"
- "Model Weights"
- "Model Checkpoints"

**NOTE**: The double quotes must be wrapped around each search query.

This data will be availible in
`./data/0_initial_study/{journal}/{search_query}/{page_number}.html` with the
exception of PLOS data. This will be made availible as
`./data/0_initial_study/{journal}/{search_query}/{page_number}.json`

### Results

Prior to computing results, it was identified that Nature, Science, PLOS search
engines return both peer-reviewed and non-peer-reviewed documents. These
documents can include news articles or procedures. We address this in the next
section.

## Refined Study

We now need to refine the search results in order to get accurate data regarding
how many *peer-reviewed* documents are returned with the aforementioned search
queiries.

To do so, we apply publisher specific refinements.

For Nature, we apply the following refinements to the search results:

- We set the "Article type" to "Research"

For PLOS we apply the following refinements to the search results:

- We set the "Article Type" to "Research Article"

**NOTE**: This requires modifying the search url to
[https://journals.plos.org/plosone/dynamicSearch?filterJournals=PLoSONE&filterArticleTypes=Research%20Article&q=](https://journals.plos.org/plosone/dynamicSearch?filterJournals=PLoSONE&filterArticleTypes=Research%20Article&q=)

For Science we apply the following reginements to the search results:

- We set the "ARTICLE TYPE" to "Research And Reviews"
- We set "PEER REVIEWED" to "Yes"

We use the same search queries as the previous section with the refinements
applied on the publishers website. We save the results to
`./data/1_refined_study/{journal}/{search_query}/{page_number}.html` with the
exception of PLOS data. This will be made availible as
`./data/1_refined_study/{journal}/{search_query}/{page_number}.json`
