n = int(input())

numbers = list(map(int, input().split( )))

numbers.sort(reverse=True)

for el in numbers:
  print(el , end = " ")