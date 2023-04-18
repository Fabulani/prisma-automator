import pandas as pd
from pybliometrics.scopus import ScopusSearch
from pybliometrics.scopus.exception import ScopusQueryError

from prisma_automator.utility import save_to_file_advanced


class Collector:
    def search(self, splits: list, subscriber: bool = False, threshold: int = 1000, log: bool = True) -> tuple[pd.DataFrame, list, list]:
        """ Identification phase of the PRISMA statement. Search through Scopus using `splits` and return results.

        `splits`: list of split search strings.
        `subscriber`: if you have an Elsevier API Key with subscriber access, set
        this to True to get access to abstract, author keywords, etc.
        `download`: if results data should be downloaded. If False, only number of
        results will be available.
        `threshold`: if number of search results goes over this value, they're 
        added to the excluded results group and ignored for the dataframe.
        """
        df = pd.DataFrame()  # Dataframe for later exporting to Excel
        search_results = []
        excluded_results = []
        num_splits = len(splits)
        i = 0
        for s in splits:
            if log:
                print(f"[#] Current Progress: {i}/{num_splits}", end="\r")
            search = "TITLE-ABS-KEY(" + s + ")"
            try:
                ss = ScopusSearch(
                    search, subscriber=subscriber, download=True)
                num_results = ss.get_results_size()  # Number of search results
                if num_results > threshold:
                    excluded_results.append((num_results, s))
                elif num_results:  # Avoid zero-result search strings
                    search_results.append((num_results, s))
                    results_df = pd.DataFrame(ss.results)
                    results_df.insert(0, 'splits', s)   # Add "splits" to df
                    df = df.append(results_df)
            except ScopusQueryError:
                excluded_results.append((">5000", s))
            i += 1
        if log:
            print(f"[$] Current Progress: {i}/{num_splits} (done)")
        return df, search_results, excluded_results

    def screen(self, df: pd.DataFrame, log: bool = True) -> pd.DataFrame:
        """ Screening phase of the PRISMA statement. Drop unnecessary columns and remove duplicates.

        `df`: a pandas dataframe containing the search results from Scopus.
        `log`: if True, prints information to the cmd prompt.
        """
        shape = df.shape
        new_shape = (0, 0)
        if log:
            print(
                f"[#] Initial dataframe with {shape[0]} rows and {shape[1]} columns. Screening...")

        # Drop unnecessary columns
        columns_to_drop = ["eid", "pii", "pubmed_id", "subtype", "afid", "affilname", "affiliation_city", "affiliation_country",
                                  "author_count", "author_ids", "author_afids", "coverDisplayDate", "issn", "source_id",
                                  "eIssn", "publicationName", "aggregationType", "article_number", "fund_acr", "fund_no", "fund_sponsor"]
        new_df = df.drop(columns=columns_to_drop)

        if log:
            print(f"[#] Dropped {len(columns_to_drop)} columns.")

        # Remove duplicates based on the title and description columns
        new_df = new_df.drop_duplicates(subset=['title', 'description'])

        if log:
            new_shape = new_df.shape
            num_duplicates = shape[0] - new_shape[0]
            print(f"[#] Removed {num_duplicates} duplicates.")
            shape = new_df.shape

        # Remove conference reviews
        new_df = new_df[new_df.subtypeDescription != "Conference Review"]

        if log:
            new_shape = new_df.shape
            num_reviews = shape[0] - new_shape[0]
            print(f"[#] Removed {num_reviews} conference reviews.")
            shape = new_df.shape

        # Remove rows without doi
        new_df = new_df[new_df['doi'].astype(bool)]

        if log:
            new_shape = new_df.shape
            num_empty_doi = shape[0] - new_shape[0]
            print(f"[#] Removed {num_empty_doi} rows without a doi.")

        if log:
            new_shape = new_df.shape
            print(
                f"[#] New dataframe with {new_shape[0]} rows and {new_shape[1]} columns.")
        return new_df

    def run(self, splits: list, save_to: str = "./out/", subscriber: bool = False, threshold: int = 1000, log: bool = True):
        """ Execute methods associated with Identification and Screening phases of the PRISMA statement

        `splits`: list of split search strings.
        `save_to`: path to directory in which result files will be saved.
        """

        print("[#] Identification: searching Scopus...")
        df, search_results, excluded_results = self.search(
            splits, subscriber=subscriber, threshold=threshold, log=log)

        if save_to:
            path_search_results = save_to + "search_results.txt"
            path_excluded_results = save_to + "excluded_results.txt"
            save_to_file_advanced(file_path=path_search_results,
                                  header="num_results,split",
                                  lines_to_write=search_results,
                                  separator=',')
            save_to_file_advanced(file_path=path_excluded_results,
                                  header="num_results,split",
                                  lines_to_write=excluded_results,
                                  separator=',')

            print(f"[/] Search results saved to: {path_search_results}")
            print(f"[/] Excluded results saved to: {path_excluded_results}")

        print("[#] Screening: cleaning dataframe...")

        new_df = self.screen(df, log=log)

        if save_to:
            path_final_results = save_to + "final_results.xlsx"
            new_df.to_excel(path_final_results)
            print(f"[/] Final results saved to: {path_final_results}")
