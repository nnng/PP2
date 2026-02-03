# Example №1
fruits = ["apple", "banana", "cherry"]
for x in fruits:
  print(x)
# Example №2
for x in "banana":
  print(x)
# Example №3
fruits = ["apple", "banana", "cherry"]
for x in fruits:
  print(x)
  if x == "banana":
    break
# Example №4
fruits = ["apple", "banana", "cherry"]
for x in fruits:
  if x == "banana":
    break
  print(x)
# Example №5
fruits = ["apple", "banana", "cherry"]
for x in fruits:
  if x == "banana":
    continue
  print(x)