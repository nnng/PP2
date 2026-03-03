n = int(input())
words = input().split()

for index, word in enumerate(words):
    print(f"{index}:{word}", end=" ")