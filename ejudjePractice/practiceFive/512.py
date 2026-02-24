import re

text = input()

numbers = sorted(map(int, re.findall(r"\d{2,}", text)))
print(" ".join(map(str, numbers)))
