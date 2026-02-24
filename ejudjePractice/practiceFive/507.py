import re

s = input()
old = input()
new = input()

result = re.sub(re.escape(old), new, s)
print(result)