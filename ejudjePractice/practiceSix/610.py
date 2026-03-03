n = int(input())
numbers = list(map(int, input().split()))

print(sum(map(bool, numbers)))