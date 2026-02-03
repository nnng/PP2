n = int(input())

operator = True
while n>1:
  if n % 2 == 0:
     n = n // 2
  else:
    operator = False
    break

print("YES") if operator == True else print("NO")
