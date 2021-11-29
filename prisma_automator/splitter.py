from prisma_automator.utility import save_to_file


class Splitter:
    def __init__(self):
        self.kw_groups = []

    def add_kwgroup(self, kw_group: list[str]):
        self.kw_groups.append(kw_group)

    def add_kwgroups(self, kw_groups: list):
        for kw_g in kw_groups:
            self.add_kwgroup(kw_g)

    def generate_kwgraph(self) -> dict:
        """ Generate a key-word adjacency graph for use in depth-first search.

        Each key-word group in `self.kw_groups` is a level in the tree, and every
        key-word is a node. All nodes from the level below the current one are children
        of all nodes in the current level.

        E.g.: 

             (A)

           (B) (C)

         (D) (E) (F)

        - (A) is the root, always an empty string `""`.
        - (B) and (C) are from the same key-word group, and both have children
        `[(D), (E), (F)]`.
        - (D), (E), and (F) are leaves, so no children: `[]`.
        """
        graph = dict()
        num_groups = len(self.kw_groups)
        prev_group = list()
        num_skips = 0
        i = 1
        for kw_g in self.kw_groups:
            if '' in kw_g:
                # If the kw is an empty string, replace it with '#' times
                # the number of skips that already happened. This guarantees
                # that the graph has unique nodes, even if there are multiple skips,
                # and avoids infinite recursion.
                num_skips += 1
                kw_g = ['#'*num_skips if x == '' else x for x in kw_g]
            if i == 1:  # First group
                graph[''] = kw_g  # Add root node connecting to the first group
            else:
                for kw in prev_group:  # For every kw of the previous group,
                    graph[kw] = kw_g   # add the current group as children
            if i == num_groups:  # Last group
                for kw in kw_g:
                    # Add the last group's kw as leaves (no children)
                    graph[kw] = list()
            prev_group = kw_g
            i += 1
        return graph

    def generate_combinations(self, temp_combination: list, combinations: list, graph: dict, node: str) -> list:
        """ Recursive Depth-first Search implementation for generating all possible key-word combinations.

        `temp_combination`: temporary list for key-word combinations
        `combinations`: list of complete key-word combinations
        `graph`: adjacency graph
        `node`: root node
        """
        temp_combination.append(node)  # Add key-word to the combination
        if not graph[node]:  # Complete combination found
            # Add combination to the list, except for root node (empty string)
            combinations.append(temp_combination[1:])
        for neighbour in graph[node]:
            self.generate_combinations(
                temp_combination, combinations, graph, neighbour)
        temp_combination.pop()  # Remove kw so that another one from the same group can be added

        # If there aren't any more combinations to be made, return
        if not temp_combination:
            return combinations

    def parse_combinations(self, combinations: list) -> list:
        """ Parse combinations and return a list of splits with logical operators

        `combinations`: list of key-word combinations
        """
        splits = list()
        for c in combinations:
            temp_split = ""
            for kw in c:
                if '#' not in kw:  # When the kw has '#', it is skipped.
                    if '||' in kw:  # kw contains OR operator. Apply different parsing.
                        temp_kw = kw.split("||")
                        temp_kw = [t_kw.strip() for t_kw in temp_kw]
                        # First t_kw must not have OR
                        kw = f"\"{temp_kw[0]}\""
                        for t_kw in temp_kw[1:]:
                            kw += f" OR \"{t_kw}\""
                        if temp_split:
                            temp_split += f" AND ({kw})"
                        else:  # First kw of the split
                            temp_split += f"({kw})"
                    else:
                        if temp_split:
                            temp_split += f" AND \"{kw}\""
                        else:  # First kw of the split
                            temp_split += f"\"{kw}\""
            splits.append(temp_split)
        return splits

    def split(self, log: bool = True, save_to: str = "./out/splits.txt") -> list:
        """ Generate split strings by combining the key-words in `kw_groups`.

        `log`: if True, prints logs.
        `save_to`: path to the file in which the splits will be written. If `""`, doesn't save a file.
        """

        if log:
            print("[#] Generating adjacency list... ")

        # Generate adjacency list as a Python dict
        graph = self.generate_kwgraph()

        temp_combination = list()  # List as a Stack to build kw combinations
        combinations = list()  # List of kw combinations

        if log:
            print("[#] Generating key-word combinations... ")

        # Generate all possible key-word combinations
        combinations = self.generate_combinations(
            temp_combination, combinations, graph, '')

        if log:
            print("[#] Generating splits... ")

        # Generate splits (search strings) from key-word combinations
        splits = self.parse_combinations(combinations)

        if log:
            print("[$] Success! Total number of splits: " + str(len(splits)))

        if save_to:
            save_to_file(file_path=save_to, lines_to_write=splits)

        return splits
