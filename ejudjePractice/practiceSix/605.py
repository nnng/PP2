s = input().lower()

if any(c in "aeiou" for c in s):
    print("Yes")
else:
    print("No")