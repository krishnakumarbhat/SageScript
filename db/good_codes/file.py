# good_practice_5.py

def get_age_from_dict(data: dict, key: str) -> int:
    """Safely retrieves and converts an age from a dictionary."""
    try:
        age_str = data[key]
        return int(age_str)
    except KeyError:
        print(f"Error: The key '{key}' was not found in the dictionary.")
        return -1
    except (ValueError, TypeError):
        print(f"Error: The value for '{key}' ('{age_str}') is not a valid integer.")
        return -1

# Example usage:
user_data = {"name": "John", "age": "30"}
print(get_age_from_dict(user_data, "age"))      # Success
print(get_age_from_dict(user_data, "city"))     # KeyError
print(get_age_from_dict({"age": "thirty"}, "age")) # ValueError