import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sample_path = os.path.join(BASE_DIR, "sample.txt")

with open(sample_path, "r", encoding="utf-8") as file:
    print(file.read())




