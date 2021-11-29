from pybliometrics.scopus import ScopusSearch
from pybliometrics.scopus.exception import ScopusQueryError
import pandas as pd


def clean_data_frame(df: pd.DataFrame):
    shape = df.shape
    print(
        f"[#] Initial dataframe with {shape[0]} columns and {shape[1]} rows. Cleaning...")
    # Drop unnecessary columns
    new_df = df.drop(columns=["eid", "pii", "pubmed_id", "subtype", "afid", "affilname", "affiliation_city", "affiliation_country",
                              "author_count", "author_ids", "author_afids", "coverDisplayDate", "issn", "source_id",
                              "eIssn", "publicationName", "aggregationType", "article_number", "fund_acr", "fund_no", "fund_sponsor"]
                     )
    # Remove duplicates
    new_df = new_df.drop_duplicates()
    shape = new_df.shape
    print(f"[#] New dataframe with {shape[0]} columns and {shape[1]} rows.")
    return new_df


df = pd.DataFrame()
search = "TITLE-ABS-KEY(\"Assembly\" AND \"Digital Twin\" AND \"Planning\")"

try:
    print("[#] Searching...")
    ss = ScopusSearch(search, subscriber=False, download=True, verbose=True)
    num_results = ss.get_results_size()  # Number of search results
    print(f"[#] Search successful: {num_results} results.")
    if num_results:  # Avoid zero-result search strings
        df = df.append(pd.DataFrame(ss.results))
        # df = pd.DataFrame(ss.results)
        print(f"[#] Created dataframe of size {df.size}.")
except ScopusQueryError:
    pass

new_df = clean_data_frame(df)
new_df.to_excel("./out/dataframe-tiny.xlsx")
