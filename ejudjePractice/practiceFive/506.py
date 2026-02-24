import re

text = input()
print(f"{(re.search(r"\S+@\S+\.\S+", text)).group()}" if re.search(r"\S+@\S+\.\S+", text) else "No email")


