import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sample_path = os.path.join(BASE_DIR, "sample.txt")

with open(sample_path, "a", encoding="utf-8") as file:
    file.write("\n")
    file.write("This is new line.\n")
    file.write("This is another new line.\n")




