import os

def save_to_file_advanced(file_path: str, header: str, lines_to_write: list[tuple[str]], separator: str = ""):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "w") as f:
        f.write(header + "\n")  # Write the header first
        for l in lines_to_write:  # then write every line
            full_line = ""
            for column in l:  # append columns to the full line
                full_line += f"{column}{separator}"
            f.write(full_line + "\n")


def save_to_file(file_path: str, lines_to_write: list[str]):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "w") as f:
        for l in lines_to_write:
            f.write(l + "\n")
