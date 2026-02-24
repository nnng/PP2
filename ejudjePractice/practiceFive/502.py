import re
str = input()
substr = input()

print( "Yes " if re.search(re.escape(substr),str) else "No")

