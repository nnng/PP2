# import os
# print(os.getcwd())
# print(os.listdir())

import json

# открываем файл
with open("Practice/PracticeFour/sample_data.json", "r") as file:
    data = json.load(file)

# заголовок
print("Interface Status")
print("=" * 80)
print(f"{'DN':50} {'Description':20} {'Speed':6} {'MTU':6}")
print("-" * 80)

# проходим по всем интерфейсам
for item in data["imdata"]:
    attributes = item["l1PhysIf"]["attributes"]
    
    dn = attributes["dn"]
    descr = attributes["descr"]
    speed = attributes["speed"]
    mtu = attributes["mtu"]

    print(f"{dn:50} {descr:20} {speed:6} {mtu:6}")
