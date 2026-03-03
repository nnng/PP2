import os
import shutil

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

#  Создаем тестовый файл 
test_file_path = os.path.join(BASE_DIR, "example.txt")

with open(test_file_path, "w", encoding="utf-8") as file:
    file.write("This is a test file.\n")

print("Тестовый файл создан.")


#  Поиск файлов с расширением .txt 
print("\nНайденные .txt файлы:")

for item in os.listdir(BASE_DIR):
    if item.endswith(".txt"):
        print(item)


# Копирование файла 
destination_folder = os.path.join(BASE_DIR, "project_data")

os.makedirs(destination_folder, exist_ok=True)

copy_path = os.path.join(destination_folder, "example_copy.txt")

shutil.copy(test_file_path, copy_path)

print("\nФайл скопирован в project_data.")


#  Перемещение файла 
move_path = os.path.join(destination_folder, "example_moved.txt")

shutil.move(test_file_path, move_path)

print("Файл перемещен в project_data.")