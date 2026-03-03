n = int(input())
numbers = list(map(int, input().split()))

s= sorted(set(numbers))
print(*s)