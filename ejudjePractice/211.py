n,l,r = map(int,input().split())

numbers = list(map(int, input().split( )))

numbers[l-1:r] = reversed(numbers[l-1:r])

for el in numbers:
  print(el , end = " ")