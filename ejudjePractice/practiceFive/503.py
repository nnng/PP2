import re
str = input()
pattern = input()

counter = 0
for i in (re.findall(pattern, str)):
  counter += 1

print(counter)
