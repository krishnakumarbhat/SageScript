# good_practice_2.py

def write_greetings(file_path: str, names: list):
    """Writes a greeting for each name to a file."""
    try:
        with open(file_path, 'w') as f:
            for name in names:
                f.write(f"Hello, {name}!\n")
        print(f"Successfully wrote greetings to {file_path}")
    except IOError as e:
        print(f"Error writing to file {file_path}: {e}")

# Example usage:
write_greetings('greetings.txt', ['Alice', 'Bob', 'Charlie'])