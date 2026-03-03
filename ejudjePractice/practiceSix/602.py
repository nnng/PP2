n = int(input())
numbers = list(map(int, input().split()))

evens = filter(lambda x: x % 2 == 0, numbers)
print(len(list(evens)))