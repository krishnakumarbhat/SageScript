"""
file_handler.py

Functions to handle file read and write operations safely.
"""

from typing import List


def read_lines(filepath: str) -> List[str]:
    """
    Read all lines from a file.

    Args:
        filepath: Path to the file.

    Returns:
        List of lines read from the file.
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            lines = file.readlines()
        return [line.strip() for line in lines]
    except FileNotFoundError:
        print(f"File not found: {filepath}")
        return []
    except IOError as error:
        print(f"IO error while reading file: {error}")
        return []


def write_lines(filepath: str, lines: List[str]) -> None:
    """
    Write a list of lines to a file.

    Args:
        filepath: Path to the file.
        lines: List of strings to write.
    """
    try:
        with open(filepath, 'w', encoding='utf-8') as file:
            for line in lines:
                file.write(f"{line}\n")
    except IOError as error:
        print(f"IO error while writing file: {error}")


if __name__ == "__main__":
    sample_lines = ["Line 1", "Line 2", "Line 3"]
    write_lines("sample.txt", sample_lines)
    read_content = read_lines("sample.txt")
    print("Read from file:")
    for line in read_content:
        print(line)
