n = int(input())

numbers = list(map(int, input().split( )))

minEl = min(numbers)
maxEl = max(numbers)

for el in numbers:
  if el == maxEl:
    numbers[numbers.index(el)] = minEl

for el in numbers:
    print(el , end = " ")

