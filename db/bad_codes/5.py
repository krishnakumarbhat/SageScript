# bad_practice_5.py

user_input = "test"
try:
    # This might fail with a ValueError if input is not a number
    # It might fail with a TypeError if you pass it `None`
    # It might fail with ZeroDivisionError if it was 0
    value = int(user_input)
    result = 100 / value
except Exception as e: # This is too broad!
    # Which error was it? We don't know without printing e.
    # It also catches errors you didn't expect, masking other bugs.
    print(f"An unknown error occurred: {e}")