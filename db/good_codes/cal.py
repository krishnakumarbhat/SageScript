"""
calculator.py

A simple calculator module demonstrating professional Python coding practices.
"""

from typing import Union


def add(a: Union[int, float], b: Union[int, float]) -> Union[int, float]:
    """Return the sum of two numbers."""
    return a + b


def subtract(a: Union[int, float], b: Union[int, float]) -> Union[int, float]:
    """Return the difference of two numbers."""
    return a - b


def multiply(a: Union[int, float], b: Union[int, float]) -> Union[int, float]:
    """Return the product of two numbers."""
    return a * b


def divide(a: Union[int, float], b: Union[int, float]) -> Union[float, None]:
    """
    Return the division of two numbers.
    
    Raises:
        ValueError: If the divisor is zero.
    """
    if b == 0:
        raise ValueError("Cannot divide by zero.")
    return a / b


if __name__ == "__main__":
    # Example usage
    try:
        print(f"10 + 5 = {add(10, 5)}")
        print(f"10 - 5 = {subtract(10, 5)}")
        print(f"10 * 5 = {multiply(10, 5)}")
        print(f"10 / 5 = {divide(10, 5)}")
    except ValueError as error:
        print(f"Error: {error}")
