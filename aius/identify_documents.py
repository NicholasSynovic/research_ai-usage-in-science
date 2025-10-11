"""
Identify PLOS documents from PLOS search results.

Copyright 2025 (C) Nicholas M. Synovic
"""

from json import loads

import pandas as pd
from progress.bar import Bar


class PLOSPaperIdentifier:
    """
    Class to identify and extract papers from PLOS search results.

    This class is designed to process the output of a PLOS search, identifying
    individual documents within each search result and mapping these back to
    their respective searches. It leverages the JSON structure returned by PLOS
    API calls to parse document details, facilitating further analysis or
    storage in relational databases. The design emphasizes modularity and
    efficiency, allowing for easy integration into larger workflows that process
    large datasets of scientific literature.

    Attributes:
        plos_search_df (DataFrame): A pandas DataFrame containing the raw output
                                        from a PLOS search. Each row represents
                                        a single search result with metadata
                                        including HTML content where document
                                        details are embedded in JSON format.
        plos_search_count (int): The total number of search results processed,
                                    determined at initialization.
        plos_searches_and_papers_df (DataFrame): A DataFrame that combines
                                                    information about PLOS
                                                    searches and the identified
                                                    papers within those
                                                    searches. This is computed
                                                    during initialization
                                                    through the
                                                    `identify_papers` method.
        plos_unique_papers_df (DataFrame): A DataFrame containing unique DOI
                                            entries extracted from all
                                            identified papers. This helps in
                                            identifying distinct documents
                                            across multiple searches, useful for
                                            deduplication or further analysis.
        searches_to_papers_mapping (DataFrame): A mapping between PLOS searches
                                                    and the papers they contain,
                                                    facilitating queries that
                                                    need to trace back from
                                                    individual papers to their
                                                    originating search.

    Methods:
        identify_papers(self) -> DataFrame: Parses each search result's HTML
                                                content, extracting DOI
                                                information for identified
                                                documents. Returns a DataFrame
                                                containing detailed mappings of
                                                searches to papers, including
                                                the unique identifiers (DOIs)
                                                and references to the original
                                                search IDs.
        get_unique_paper_dois(self) -> DataFrame: Extracts unique DOI values
                                                    from all identified papers,
                                                    ensuring no duplicate
                                                    entries are present in the
                                                    output. This is useful for
                                                    operations that require a
                                                    list of distinct documents,
                                                    such as deduplication or
                                                    aggregation across searches.
        map_searches_to_papers(self) -> DataFrame: Constructs a mapping between
                                                    each PLOS search and its
                                                    associated identified
                                                    papers. Returns a DataFrame
                                                    where each row represents a
                                                    paper with columns
                                                    indicating the originating
                                                    search ID(s) and the paper's
                                                    DOI, enabling easy lookup of
                                                    which searches contributed
                                                    to specific documents.

    Notes:
        The methods within this class are designed to be called sequentially as
        part of a larger workflow, starting from raw PLOS search results through
        to structured mappings of papers across searches. This sequential
        approach ensures that each transformation step builds upon the previous
        one, progressively refining the dataset for downstream analysis or
        storage.

    """

    def __init__(self, plos_search_df: pd.DataFrame) -> None:
        """Instantiate the class and run the analysis."""
        # Store class variables
        self.plos_search_df: pd.DataFrame = plos_search_df
        self.plos_search_count: int = self.plos_search_df.shape[0]

        # Run the analysis
        self.plos_searches_and_papers_df: pd.DataFrame = self.identify_papers()
        self.plos_unique_papers_df: pd.DataFrame = self.get_unique_paper_dois()
        self.searches_to_papers_mapping: pd.DataFrame = self.map_searches_to_papers()

    def identify_papers(self) -> pd.DataFrame:
        """
        Parse each search result to extract DOIs.

        This method is the core of the PLOSPaperIdentifier class. It iterates
        over each row in `plos_search_df`, which represents a single search
        result from PLOS. For each search result, it parses the embedded JSON to
        extract document details, specifically focusing on DOI information. The
        extracted DOIs are then mapped back to their respective searches,
        allowing for a detailed reconstruction of how individual documents
        relate to specific searches.

        Returns:
            DataFrame: A pandas DataFrame containing mappings between PLOS
                        searches and identified papers, including unique
                        identifiers (DOIs) for each paper. This structure
                        facilitates further analysis or storage in relational
                        databases, enabling queries that trace back from
                        individual papers to their originating search IDs.

        """
        # Setup variables to store data
        identified_paper_dfs: list[pd.DataFrame] = []
        datum_template: dict[str, list] = {"search_id": [], "doi": []}

        with Bar(
            "Identifying papers from PLOS searches...",
            max=self.plos_search_count,
        ) as bar:
            row: pd.Series
            for _, row in self.plos_search_df.iterrows():
                # Copy template for each search result
                datum: dict[str, list] = datum_template.copy()

                # Get JSON object
                json_str: str = row["html"]
                json_dict: dict = loads(s=json_str)

                # Parse JSON for DOIs
                docs: list[dict] = json_dict["searchResults"]["docs"]
                doc: dict
                for doc in docs:
                    datum["search_id"].append(row["_id"])
                    datum["doi"].append(f"https://doi.org/{doc['id']}")

                # Create DataFrame of results and append it to the list
                identified_paper_dfs.append(pd.DataFrame(data=datum))

                bar.next()

        # Drop duplicates if an entire row is the same. Covers the edge case
        # where a single search result returns duplicate paper results
        return pd.concat(
            objs=identified_paper_dfs,
            ignore_index=True,
        ).drop_duplicates(ignore_index=True)

    def get_unique_paper_dois(self) -> pd.DataFrame:
        """
        Extract unique DOI values from identified papers.

        This method takes the combined DataFrame of searches and their
        associated papers (`plos_searches_and_papers_df`) and extracts a list of
        unique DOI entries. The goal is to identify distinct documents across
        multiple searches, which helps in deduplication efforts or when
        aggregating data across different sources that might otherwise contain
        duplicate records.

        Returns:
            DataFrame: A pandas DataFrame containing unique DOI values extracted
                        from all identified papers. This DataFrame is useful for
                        operations requiring a list of distinct documents, such
                        as deduplication processes or further analysis that
                        requires unique entries only.

        """
        return self.plos_searches_and_papers_df[["doi"]].drop_duplicates(
            keep="first",
            ignore_index=True,
        )

    def map_searches_to_papers(self) -> pd.DataFrame:
        """
        Construct a mapping between PLOS searches and their papers.

        This method creates a detailed mapping that links every paper back to
        the original searches from which they were extracted. It involves
        joining the DataFrame containing unique DOI entries
        (`plos_unique_papers_df`) with the combined DataFrame of searches and
        their papers (`plos_searches_and_papers_df`) on the shared DOI column,
        effectively tracing each paper's origin back to its source search.

        Returns:
            DataFrame: A pandas DataFrame where each row represents a paper with
                        columns indicating the originating search ID(s) and the
                        paper's DOI. This structure is particularly useful for
                        queries that need to trace back from individual papers
                        to their originating searches, facilitating complex
                        analyses or reports that require contextual information
                        about how specific documents were identified within
                        larger datasets.

        """
        # Create a copy of the unique papers DataFrame
        doi_df: pd.DataFrame = self.plos_unique_papers_df.copy()

        # Create a copy of the searches and papers DataFrame
        search_to_paper_df: pd.DataFrame = self.plos_searches_and_papers_df.copy()

        # Swap the index of doi_df with the doi column
        doi_df = doi_df.reset_index(names="paper_id").set_index(keys="doi")

        # Join doi_df to search_to_paper by shared doi column
        return search_to_paper_df.join(doi_df, on="doi").drop(columns="doi")
