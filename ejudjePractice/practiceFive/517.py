import re

s = input()
pattern = r"\b\d{2}/\d{2}/\d{4}\b"
print(len(re.findall(pattern, s)))