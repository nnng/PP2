import re

text = input()

matches = re.findall(r"\b\w{3}\b", text)

print(len(matches))