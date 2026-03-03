import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


nested_path = os.path.join(BASE_DIR, "project_data", "logs")

# Создание вложенных папок
os.makedirs(nested_path, exist_ok=True)

print("Вложенные папки созданы.")


#  Вывод списка файлов и папок 
print("\n directory_management:")

for item in os.listdir(BASE_DIR):
    full_path = os.path.join(BASE_DIR, item)

    if os.path.isdir(full_path):
        print(f"{item} - папка")
    else:
        print(f"{item} - файл")