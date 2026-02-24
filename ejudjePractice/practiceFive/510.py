import re

text = input()

if re.search(r"cat|dog", text):
    print("Yes")
else:
    print("No")