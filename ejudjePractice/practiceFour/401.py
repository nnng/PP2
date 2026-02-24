def sq_generator(n):
  for i in range(1,n+1):
    yield i**2

n = int(input())
for el in sq_generator(n):
  print(el)