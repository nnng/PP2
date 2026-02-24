import re

s = input()
p=input()
matches = re.findall(re.escape(p), s)
print(len(matches))