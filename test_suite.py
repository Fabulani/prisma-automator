import pytest
from prisma_automator.splitter import Splitter


class TestSplitter():
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
