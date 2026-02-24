import re

text = input()

res = re.findall(r"\w+",text)

print(len(res))
