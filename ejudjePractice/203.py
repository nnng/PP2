n = int(input())

numbers = list(map(int, input().split( )))

sum = 0
for i in range(n):
  sum += numbers[i]

print(sum)