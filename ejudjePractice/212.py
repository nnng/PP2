n= int(input())

numbers = list(map(int, input().split( )))

for el in numbers:
  print(el**2 , end = " ")