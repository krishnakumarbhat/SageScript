"""
string_utils.py

Utility functions for string manipulation.
"""

from typing import List


def reverse_string(s: str) -> str:
    """Return the reversed version of the input string."""
    return s[::-1]


def capitalize_words(s: str) -> str:
    """Capitalize the first letter of each word in the string."""
    return ' '.join(word.capitalize() for word in s.split())


def find_substrings(s: str, substring: str) -> List[int]:
    """
    Find all start indices of substring in s.

    Args:
        s: The string to search within.
        substring: The substring to find.

    Returns:
        List of starting indices where substring is found.
    """
    indices = [i for i in range(len(s)) if s.startswith(substring, i)]
    return indices


if __name__ == "__main__":
    test_string = "hello world, hello python"
    print(f"Original: {test_string}")
    print(f"Reversed: {reverse_string(test_string)}")
    print(f"Capitalized: {capitalize_words(test_string)}")
    print(f"Indices of 'hello': {find_substrings(test_string, 'hello')}")
