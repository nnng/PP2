import re

text = input()

pattern = r'Name:\s*(.+),\s*Age:\s*(.+)'

match = re.search(pattern, text)

if match:
    print(match.group(1), match.group(2))