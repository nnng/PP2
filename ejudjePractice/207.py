
n = int(input())

numbers = list(map(int, input().split( )))

print(numbers.index(max(numbers)) + 1)