import re
str = input()

print( "Yes " if re.match("^Hello",str) else "No")

