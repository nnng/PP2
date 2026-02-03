n = int(input())

print("YES") if (n % 4 == 0 and n % 100 != 0) or (n % 400 == 0) else print("NO")