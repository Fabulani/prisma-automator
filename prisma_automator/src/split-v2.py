def make_header(title: str, weight: int = 1):
    bars = "===="
    return "\n" + bars*weight + "[ " + title + " ]" + bars*weight + "\n"


def generate_split_string(print_report: bool = True):
    optimization = [" \"Operations Research\"", " \"Heuristics\"", " \"Particle Swarm\"",
                    " \"Linear Programming\"", " \"Mixed Integer Linear Programming\""]
    flexibility = [
        " (\"Matrix\" OR \"Modular\" OR \"Adaptive\" OR \"Flexible\" OR \"Reconfigurable\")",
        " \"Matrix\"", " \"Modular\"", " \"Adaptive\"", " \"Flexible\"", " \"Reconfigurable\"",
        ""
    ]
    production = [" (\"Manufacturing\" OR \"Assembly\" OR \"Production\")",
                  " \"Manufacturing\"", " \"Assembly\"", " \"Production\""]
    planning = [
        " \"Planning\"", " \"Configuration\"", " \"Capability\"",
        " \"Ramp-up\"", ""
    ]
    others = [" \"Digital Twin\"", ""]

    # Generate split strings
    split_strings = []
    current_string = ""

    for opt in optimization:
        for flex in flexibility:
            for prod in production:
                for plan in planning:
                    for other in others:
                        # Build the current string
                        current_string = opt
                        if flex:
                            current_string += " AND " + flex
                        if prod:
                            current_string += " AND " + prod
                        if plan:
                            current_string += " AND " + plan
                        if other:
                            current_string += " AND " + other

                        # Append to the list of split string
                        split_strings.append(current_string)
    if print_report:
        print("[#] Total number of splits: " + str(len(split_strings)))
    return split_strings


def save_splits_to_file(split_strings: list[str]):
    # Write to file
    with open("./out/splits-v2.txt", "w") as f:
        for s in split_strings:
            f.write(s + "\n")
