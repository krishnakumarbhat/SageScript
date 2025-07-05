# bad_practice_4.py

# WARNING: This function has a dangerous bug.
def add_item(item, a_list=[]):
    a_list.append(item)
    return a_list

list1 = add_item("apple")
print(list1)  # Expected: ['apple'], Actual: ['apple'] - So far so good...

list2 = add_item("banana") # This reuses the SAME list from the first call!
print(list2)  # Expected: ['banana'], Actual: ['apple', 'banana'] - BUG!