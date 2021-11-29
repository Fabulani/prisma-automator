from pybliometrics.scopus import ScopusSearch
from pybliometrics.scopus.exception import ScopusQueryError
import pandas as pd
from datetime import datetime


def clean_data_frame(df: pd.DataFrame):
    # Drop unnecessary columns
    new_df = df.drop(columns=["eid", "pii", "pubmed_id", "subtype", "afid", "affilname", "affiliation_city", "affiliation_country",
                              "author_count", "author_ids", "author_afids", "coverDisplayDate", "issn", "source_id",
                              "eIssn", "publicationName", "aggregationType", "article_number", "fund_acr", "fund_no", "fund_sponsor"]
                     )
    # Remove duplicates
    new_df = new_df.drop_duplicates()
    return new_df


def main():
    print("[$] Program start.")

    now = datetime.now()  # current date and time
    date_time = now.strftime("%Y.%m.%d_%H-%M-%S")

    split_strings = generate_split_string()
    save_splits_to_file(f"splits-v2.txt", split_strings)

    df = pd.DataFrame()
    search_results = []  # List of tuples: (num_results, split_string)
    failed_results = []
    num_splits = len(split_strings)
    i = 0

    for s in split_strings:
        print(f"[#] Current Progress: {i}/{num_splits}", end="\r")
        search = "TITLE-ABS-KEY(" + s + ")"
        try:
            ss = ScopusSearch(search, subscriber=False, download=True)
            num_results = ss.get_results_size()  # Number of search results
            if num_results:  # Avoid zero-result search strings
                search_results.append((num_results, s))
                df = df.append(pd.DataFrame(ss.results))
        except ScopusQueryError:
            failed_results.append((">5000", s))
        i += 1

    save_search_results_to_file(
        f_name=f"results.txt", search_results=search_results)

    save_search_results_to_file(
        f_name=f"failed_results.txt", search_results=failed_results)

    # Clean dataframe by removing columns and duplicates
    shape = df.shape
    print(
        f"[#] Initial dataframe with {shape[0]} columns and {shape[1]} rows. Cleaning...")
    new_df = clean_data_frame(df)
    shape = new_df.shape
    print(f"[#] New dataframe with {shape[0]} columns and {shape[1]} rows.")

    # Save to Excel file
    new_df.to_excel(f"./out/dataframe.xlsx")

    print("[$] Success.")


if __name__ == "__main__":
    main()
