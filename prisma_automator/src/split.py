AND = "\" AND \""
AND2 = "AND"
OR = "\" OR \""

# Varying
optimization = [
    "Discrete Optimization",
    "Operations Research",
    "Linear Programming",
    "Simulation"]
planning = [
    "Integration Planning",
    "Configuration Planning",
    "Capability Planning",
    "Product Planning"
]
production = [
    "Production",
    "Manufacturing",
    "Assembly"]

# 1 fixed
DT = "Digital Twin"

# 2 fixed
flexible = ["Matrix",
            "Modular",
            "Adaptive",
            "Flexible",
            "Reconfigurable"]

# Generate string with all terms of "flexible" separated by OR
# out: ("Matrix" OR "Modular" OR "Adaptive" OR "Flexible" OR "Reconfigurable")


def all_or(terms):
    all_or = ""
    i = 0
    for t in terms:
        if i == 0:
            all_or += "(\"" + t
        elif i == len(flexible)-1:
            all_or += OR + t + "\")"
        else:
            all_or += OR + t
        i += 1
    return all_or


flexible_all = all_or(flexible)

# flex1 = "(Matrix OR Modular)"
# flex2 = "(Matrix OR Adaptive)"
# flex3 = "(Matrix OR Flexible)"
# flex4 = "(Modular OR Adaptive)"
# flex5 = "(Modular OR Flexible)"
# flex6 = "(Adaptive OR Flexible)"
# flexible = [flex1, flex2, flex3, flex4, flex5, flex6]
# flexible = ["(\"Matrix\" OR \"Flexible\")"]

# Generate split strings
split_strings = []

for x in optimization:
    for y in planning:
        for z in production:

            # Case 0: no digital twin
            split_strings.append("\"" + x +
                                 AND + y +
                                 AND + z +
                                 AND + flexible_all
                                 )

            # Case 1: digital twin

            for f in flexible:
                split_strings.append("\"" + x +
                                     AND + y +
                                     AND + z +
                                     AND + DT +
                                     "\" AND " + flexible_all
                                     )

with open("splits.txt", "w") as f:
    for s in split_strings:
        f.write(s + "\n")

print("[#] Total number of splits: " + str(len(split_strings)))
