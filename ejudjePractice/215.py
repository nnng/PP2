n= int(input())

surnames = []
for i in range(n):
  element = str(input())
  surnames.append(element)
# surnames = list(map(str, input().split( )))

surnamesdict = {}

for el in surnames:
  if el in surnamesdict:
    surnamesdict[el] += 1
  else:
    surnamesdict[el] = 1

counter = 0
for key,value in surnamesdict.items():
  counter += 1

print(counter)