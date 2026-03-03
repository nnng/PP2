n = int(input())
a = list(map(int, input().split()))
b = list(map(int, input().split()))

s= sum(x * y for x, y in zip(a, b))
print(s)