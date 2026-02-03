n= int(input())

strings = []
for i in range(n):
  element = input().strip()
  strings.append(element)



stringsdict = {}

for i in range(len(strings)):
  if strings[i] in stringsdict:
    continue
  else:
    stringsdict[strings[i]] = i + 1


res = []
for key,value in stringsdict.items():
  res.append([key , value])

arr = sorted(res)

for el in arr:
  print(el[0] , el[1])