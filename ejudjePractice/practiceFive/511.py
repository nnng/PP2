import re

str = input()


counter = 0 
for el in re.findall("[A-Z]",str):
  counter += 1
print(counter)