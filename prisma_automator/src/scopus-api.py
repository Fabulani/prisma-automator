from pybliometrics.scopus import ScopusSearch
search = "TITLE-ABS-KEY(\"Digital Twin\" AND \"Assembly\")"
s = ScopusSearch(search, subscriber=False, download=False)
print(s.get_results_size())
