#example 1 from w3School
x = lambda a : a + 10
print(x(5))
#example 2 from w3School
x = lambda a, b : a * b
print(x(5, 6))
#example 3 from w3School
x = lambda a, b, c : a + b + c
print(x(5, 6, 2))
#example 4 from w3School
def myfunc(n):
  return lambda a : a * n
#example 5 from w3School
def myfunc(n):
  return lambda a : a * n

mydoubler = myfunc(2)

print(mydoubler(11))
