# good_practice_4_module.py

def useful_function():
    """A function that might be imported by other scripts."""
    print("This is a useful function from the module.")
    return 42

def main():
    """Main logic to run when the script is executed directly."""
    print("This script is being run directly.")
    result = useful_function()
    print(f"The result was {result}.")

# This code only runs when you execute `python good_practice_4_module.py`
if __name__ == '__main__':
    main()