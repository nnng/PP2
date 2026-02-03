n= int(input())

telnumbers = []
for i in range(n):
  element = input().strip()
  telnumbers.append(element)


telnumbersdict = {}

for el in telnumbers:
  if el in telnumbersdict:
    telnumbersdict[el] += 1
  else:
    telnumbersdict[el] = 1




counter = 0
maxFreq = max(telnumbersdict.values())


counter = 0
for el in telnumbersdict:
  if telnumbersdict[el] == maxFreq:
    counter += 1



print(counter)