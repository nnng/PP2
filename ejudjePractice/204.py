n = int(input())

numbers = list(map(int, input().split( )))

counter = 0
for element in numbers:
  if element > 0:
    counter += 1

print(counter)