n = int(input())


boolean = True
for i in range(1,n):
  if n % i == 0 and (i != 1 and i != n):
      boolean = False
      break

print("Yes") if boolean == True else print("No")