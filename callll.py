from typing import Union, List

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

def calculator():
    """A simple calculator module demonstrating professional Python coding practices."""
    print("Select operation:")
    print("1. Addition")
    print("2. Subtraction")
    print("3. Multiplication")
    print("4. Division")

    while True:
        choice = input("Enter your choice (1/2/3/4): ")

        if choice in ('1', '2', '3', '4'):
            num1 = float(input("Enter first number: ")))
            num2 = float(input("Enter second number: ")))

            if choice == '1':
                print(f"{num1} + {num2} = {add(num1, num2)}")
            elif choice == '2':
                print(f"{num1} - {num2} = {subtract(num1, num2)}")
    except ValueError:
        print("Invalid input. Please enter a number.")
# ```
# This code defines a `Student` class that represents a student with name and grades as attributes. The `get_top_student` function takes a list of `Student` objects and returns the student with the highest average grade. The `calculator` function displays a menu of calculator operations and prompts the user to enter two numbers for each operation. The code also includes error handling for invalid input, such as non-numeric values or division by zero.

# To use this calculator module, you can simply import it into your Python script and call the `calculator` function.

# Here's an example of how to use the calculator module:
# ```python
import 


# Call the calculator() function to display the menu
calculator_module.calculator()