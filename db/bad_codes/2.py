# bad_practice_2.py

# This is risky!
f = open('output.txt', 'w')
# If an error happens on the next line, f.close() is never called!
f.write('some data')
# Forgetting this line is a common bug.
f.close()