import re
import argparse


def check_indentation(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    for i, line in enumerate(lines):
        # Check if line starts with whitespace followed immediately by §
        match = re.match(r"^(\s+)§", line)
        if match:
            spaces = match.group(1)
            count = len(spaces)
            if count != 10:
                print(f"Anomaly in {file_path} at line {i+1}: Found {count} spaces.")
                print(f"Content: {line.strip()}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Check indentation of § symbols in a text file."
    )
    parser.add_argument("file_path", help="Path to the text file to check")
    args = parser.parse_args()

    check_indentation(args.file_path)
