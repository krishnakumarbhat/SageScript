# bad_practice_3.py

numbers = [1, 2, 3, 4, 5, 6]
squared_even_numbers = []
for n in numbers:
    if n % 2 == 0:
        squared_even_numbers.append(n**2)

print(squared_even_numbers)