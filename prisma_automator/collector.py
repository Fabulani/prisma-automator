from pybliometrics.scopus import ScopusSearch
from pybliometrics.scopus.exception import ScopusQueryError
import pandas as pd
from prisma_automator.utility import save_to_file_advanced


class Collector:
    def screen(self, df: pd.DataFrame, log: bool = True) -> pd.DataFrame:
        """ Screening phase of the PRISMA statement. Drop unnecessary columns and remove duplicates.

        `df`: a pandas dataframe containing the search results from Scopus.
        `log`: if True, prints information to the cmd prompt.
        """
        shape = df.shape
        if log:
            print(
                f"[#] Initial dataframe with {shape[0]} rows and {shape[1]} columns. Cleaning...")

        # Drop unnecessary columns
        new_df = df.drop(columns=["eid", "pii", "pubmed_id", "subtype", "afid", "affilname", "affiliation_city", "affiliation_country",
                                  "author_count", "author_ids", "author_afids", "coverDisplayDate", "issn", "source_id",
                                  "eIssn", "publicationName", "aggregationType", "article_number", "fund_acr", "fund_no", "fund_sponsor"]
                         )
        # Remove duplicates
        new_df = new_df.drop_duplicates()

        if log:
            num_duplicates = shape[0] - new_df.shape[0]
            print(f"[#] Removed {num_duplicates} duplicates.")

        if log:
            shape = new_df.shape
            print(
                f"[#] New dataframe with {shape[0]} rows and {shape[1]} columns.")
        return new_df

    def search(self, splits: list, subscriber: bool = False, download: bool = True, threshold: int = 1000) -> tuple[pd.DataFrame, list, list]:
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
            print(f"[#] Current Progress: {i}/{num_splits}", end="\r")
            search = "TITLE-ABS-KEY(" + s + ")"
            try:
                ss = ScopusSearch(
                    search, subscriber=subscriber, download=download)
                num_results = ss.get_results_size()  # Number of search results
                if num_results > threshold:
                    excluded_results.append((num_results, s))
                elif num_results:  # Avoid zero-result search strings
                    search_results.append((num_results, s))
                    df = df.append(pd.DataFrame(ss.results))
            except ScopusQueryError:
                excluded_results.append((">5000", s))
            i += 1
        print(f"[$] Current Progress: {i}/{num_splits}")
        return df, search_results, excluded_results

    def run(self, splits: list, save_to: str = "./out/"):
        """ Execute methods associated with Identification and Screening phases of the PRISMA statement

        `splits`: list of split search strings.
        """

        print("[#] Identification: searching Scopus...")
        df, search_results, excluded_results = self.search(splits)

        if save_to:
            print("[#] Saving search results...")
            save_to_file_advanced(file_path=save_to+"search_results.txt",
                                  header="num_results,split",
                                  lines_to_write=search_results,
                                  separator=',')
            save_to_file_advanced(file_path=save_to+"excluded_results.txt",
                                  header="num_results,split",
                                  lines_to_write=excluded_results,
                                  separator=',')

        print("[#] Screening: cleaning dataframe...")

        new_df = self.screen(df)

        if save_to:
            print("[#] Saving dataframe to Excel...")
            new_df.to_excel(save_to + "dataframe.xlsx")

        print("[$] Success!")
        pass
