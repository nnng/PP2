n= int(input())

numbers = list(map(int, input().split( )))


numbersDict = {}
for el in numbers:
  if el in numbersDict:
    numbersDict[el] += 1
  else:
    numbersDict[el] = 1


maxFreq = max(numbersDict.values())


ElWithMaxFreq = {}
for el in numbersDict:
  if numbersDict[el] == maxFreq:
    ElWithMaxFreq[el] = maxFreq

sorted_ElWithMaxFreq = dict(sorted(ElWithMaxFreq.items()))

print(next(iter(sorted_ElWithMaxFreq)))