import re
import os
import json

BASE_DIR = os.path.dirname(__file__)
FILE_PATH = os.path.join(BASE_DIR, "test.txt")

with open(FILE_PATH, "r", encoding="utf-8") as file:
    text = file.read()

  
res = re.findall(r"^\s*<start_time>(\d*:\d*[AMP]+)",text,re.MULTILINE|re.I)
print(res)

# // {название: {цена:}
# // общая сумма
# // способ оплаты}