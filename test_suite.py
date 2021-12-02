import pytest

from prisma_automator.collector import Collector
from prisma_automator.splitter import Splitter


class TestSplitter:
    @pytest.fixture
    def create_splitter(self):
        self.splitter = Splitter()

    @pytest.fixture
    def create_splitter_with_kwgroups(self, create_splitter):
        self.kw_groups = [["Operations Research", "Heuristics"], [
            "Flexible", "Matrix", "Reconfigurable"], ["Assembly"]]
        self.splitter.add_kwgroups(self.kw_groups)

    def test_add_kwgroup(self, create_splitter):
        kw_group = ["Operations Research", "Heuristics"]
        self.splitter.add_kwgroup(kw_group)
        assert self.splitter.kw_groups[0] == kw_group

    def test_add_kwgroups(self, create_splitter):
        kw_groups = [["Operations Research", "Heuristics"], [
            "Flexible", "Matrix", "Reconfigurable"], ["Assembly"]]
        self.splitter.add_kwgroups(kw_groups)
        assert self.splitter.kw_groups == kw_groups

    def test_generate_kwgraph(self, create_splitter_with_kwgroups):
        expected_graph = {
            "": ["Operations Research", "Heuristics"],
            "Operations Research": ["Flexible", "Matrix", "Reconfigurable"],
            "Heuristics": ["Flexible", "Matrix", "Reconfigurable"],
            "Flexible": ["Assembly"],
            "Matrix": ["Assembly"],
            "Reconfigurable": ["Assembly"],
            "Assembly": []
        }
        graph = self.splitter.generate_kwgraph()
        assert graph == expected_graph

    def test_generate_combinations(self, create_splitter_with_kwgroups):
        expected_combinations = [
            ['Operations Research', 'Flexible', 'Assembly'],
            ['Operations Research', 'Matrix', 'Assembly'],
            ['Operations Research', 'Reconfigurable', 'Assembly'],
            ['Heuristics', 'Flexible', 'Assembly'],
            ['Heuristics', 'Matrix', 'Assembly'],
            ['Heuristics', 'Reconfigurable', 'Assembly']
        ]
        graph = self.splitter.generate_kwgraph()
        temp_combination = list()
        combinations = list()
        combinations = self.splitter.generate_combinations(
            temp_combination, combinations, graph, '')
        assert combinations == expected_combinations

    def test_split(self, create_splitter_with_kwgroups):
        expected_splits = [
            "\"Operations Research\" AND \"Flexible\" AND \"Assembly\"",
            "\"Operations Research\" AND \"Matrix\" AND \"Assembly\"",
            "\"Operations Research\" AND \"Reconfigurable\" AND \"Assembly\"",
            "\"Heuristics\" AND \"Flexible\" AND \"Assembly\"",
            "\"Heuristics\" AND \"Matrix\" AND \"Assembly\"",
            "\"Heuristics\" AND \"Reconfigurable\" AND \"Assembly\""
        ]
        splits = self.splitter.split(log=False, save_to="")
        assert sorted(splits) == sorted(expected_splits)

    def test_split_empty_string_kw(self, create_splitter_with_kwgroups):
        expected_splits = [
            "\"Operations Research\" AND \"Flexible\" AND \"Assembly\"",
            "\"Operations Research\" AND \"Matrix\" AND \"Assembly\"",
            "\"Operations Research\" AND \"Reconfigurable\" AND \"Assembly\"",
            "\"Heuristics\" AND \"Flexible\" AND \"Assembly\"",
            "\"Heuristics\" AND \"Matrix\" AND \"Assembly\"",
            "\"Heuristics\" AND \"Reconfigurable\" AND \"Assembly\"",
            "\"Operations Research\" AND \"Flexible\" AND \"Assembly\" AND \"Digital Twin\"",
            "\"Operations Research\" AND \"Matrix\" AND \"Assembly\" AND \"Digital Twin\"",
            "\"Operations Research\" AND \"Reconfigurable\" AND \"Assembly\" AND \"Digital Twin\"",
            "\"Heuristics\" AND \"Flexible\" AND \"Assembly\" AND \"Digital Twin\"",
            "\"Heuristics\" AND \"Matrix\" AND \"Assembly\" AND \"Digital Twin\"",
            "\"Heuristics\" AND \"Reconfigurable\" AND \"Assembly\" AND \"Digital Twin\""
        ]
        kw_group = ["Digital Twin", ""]
        self.splitter.add_kwgroup(kw_group)
        splits = self.splitter.split(log=False, save_to="")
        assert sorted(splits) == sorted(expected_splits)

    def test_split_kw_with_OR_operator(self):
        expected_splits = [
            "\"Operations Research\" AND \"Flexible\"",
            "\"Operations Research\" AND (\"Flexible\" OR \"Matrix\")",
            "\"Heuristics\" AND \"Flexible\"",
            "\"Heuristics\" AND (\"Flexible\" OR \"Matrix\")",
        ]
        self.splitter = Splitter()
        self.kw_groups = [
            ["Operations Research", "Heuristics"],
            ["Flexible", "Flexible || Matrix"]
        ]
        self.splitter.add_kwgroups(self.kw_groups)
        splits = self.splitter.split(log=False, save_to="")
        assert sorted(splits) == sorted(expected_splits)


class TestCollector:
    """  Tests for the Collector class

    - NOTE: these tests take longer to complete because it has API calls. The results
    should be saved to memory after the first run.
    """
    @pytest.fixture
    def create_collector_and_splits(self):
        """

        The chosen splits return at least 1 result, but always very few, so that
        the search can be executed quickly. It's known that the number of results
        can change in the future, but this is the best way found to test the
        Collector's methods. As of 02.12.21, total results are 2 + 2 + 23 = 27.

        - NOTE: there's a repeated split for the sake of testing the remove duplicates
        functionality of the screen() method.

        """

        self.splits = [
            "\"Digital Twin\" AND \"Augmented Reality\"",
            "\"Digital Twin\" AND \"Augmented Reality\"",
            "\"Virtual Reality\"  AND  \"BCI\"  AND  \"Gaming\""
        ]
        self.collector = Collector()

    def test_search_results_df_has_all_expected_columns(self, create_collector_and_splits):
        # NOTE: "splits" column is added by the search method.
        expected_columns = ['splits', 'eid', 'doi', 'pii', 'pubmed_id', 'title', 'subtype',
                            'subtypeDescription', 'creator', 'afid', 'affilname',
                            'affiliation_city', 'affiliation_country', 'author_count',
                            'author_names', 'author_ids', 'author_afids', 'coverDate',
                            'coverDisplayDate', 'publicationName', 'issn', 'source_id', 'eIssn',
                            'aggregationType', 'volume', 'issueIdentifier', 'article_number',
                            'pageRange', 'description', 'authkeywords', 'citedby_count',
                            'openaccess', 'fund_acr', 'fund_no', 'fund_sponsor']
        all_results = self.collector.search(
            splits=self.splits, subscriber=False, download=True, threshold=1000, log=False)
        df = all_results[0]
        assert all(column in df for column in expected_columns) and len(
            df.columns) == len(expected_columns)

    def test_screen_dropped_unnecessary_columns(self, create_collector_and_splits):
        expected_columns = ['splits', 'doi', 'title', 'subtypeDescription', 'creator',
                            'author_names', 'coverDate', 'volume', 'issueIdentifier', 'pageRange',
                            'description', 'authkeywords', 'citedby_count', 'openaccess']
        all_results = self.collector.search(
            splits=self.splits, subscriber=False, download=True, threshold=1000, log=False)
        df = all_results[0]
        screened_df = self.collector.screen(df=df, log=False)
        assert all(column in screened_df for column in expected_columns) and len(
            screened_df.columns) == len(expected_columns)

    def test_screen_removed_conference_reviews(self, create_collector_and_splits):
        all_results = self.collector.search(
            splits=self.splits, subscriber=False, download=True, threshold=1000, log=False)
        df = all_results[0]
        screened_df = self.collector.screen(df=df, log=False)
        assert 'Conference Review' not in screened_df.subtypeDescription.unique()

    def test_screen_removed_duplicates(self, create_collector_and_splits):
        """
        Duplicates in this test are checked with both "doi" and "title" columns.
        """
        all_results = self.collector.search(
            splits=self.splits, subscriber=False, download=True, threshold=1000, log=False)
        df = all_results[0]
        screened_df = self.collector.screen(df=df, log=False)
        num_duplicates = screened_df.duplicated(subset=['doi', 'title']).sum()
        assert num_duplicates == 0

    def test_screen_removed_rows_without_doi(self, create_collector_and_splits):
        """
        NOTE: test needs to be improved! It'll always pass for the current splits.
        TODO: instead of using collector.search() to get the dataframe, create
        the dataframe manually and then screen it.
        """
        all_results = self.collector.search(
            splits=self.splits, subscriber=False, download=True, threshold=1000, log=False)
        df = all_results[0]
        screened_df = self.collector.screen(df=df, log=False)
        assert '' not in screened_df.doi.unique()
