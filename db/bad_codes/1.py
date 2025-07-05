# bad_practice_1.py

# What does this function do?
def proc_data(l, f):
    res = sum(l)
    return res * (1 + f)

# Usage is unclear without inspecting the function
my_list = [10.5, 25.0, 7.99]
print(proc_data(my_list, 0.08))