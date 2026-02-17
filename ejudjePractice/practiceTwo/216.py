n= int(input())


numbers = list(map(str, input().split( )))

numbersDict = {}

for el in numbers:
  if el in numbersDict:
    print("NO")
  else:
    numbersDict[el] = 1
    print("YES")



