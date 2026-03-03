import os
import shutil

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sample_path = os.path.join(BASE_DIR, "sample.txt")
copy_path = os.path.join(BASE_DIR, "sample_copy.txt")

shutil.copy(sample_path, copy_path)

print("\nФайл скопирован в sample_copy.txt")

file_to_delete = copy_path
check = bool(input("Delete file?"))
if (os.path.exists(file_to_delete) and check == True):
    os.remove(file_to_delete)
    print(f"\nФайл {file_to_delete} удален.")
else:
    print(f"\nФайл {file_to_delete} не найден.")




