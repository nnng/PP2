import re
import os
import json

BASE_DIR = os.path.dirname(__file__)
FILE_PATH = os.path.join(BASE_DIR, "raw.txt")

with open(FILE_PATH, "r", encoding="utf-8") as file:
    text = file.read()


names = re.findall("^\d+\.\s(^.*$)",text,re.MULTILINE | re.I)

prices = (re.findall("^Стоимость\n(\d+)",text,re.MULTILINE))
# print(f"prices: \n {prices} \n")


totalCost = 0
for el in prices:
  totalCost +=int(el)
payment = re.findall("Банк\w*\s*\w*|Налич\w*",text,re.MULTILINE| re.I)

res = []
for i in range(len(prices)):
    res.append(f"Название : {names[i]} \n Цена : {prices[i]} \n")
res.append(f"Общая сумма : {totalCost} \n Способ оплаты : {payment}")


with open("Practice/PracticeFive/output.json", "w", encoding="utf-8") as file:
    json.dump(res, file, ensure_ascii=False, indent=4)
