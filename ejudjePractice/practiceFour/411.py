import json
import sys

def apply_patch(source, patch):
    for key in patch:
        # Если значение null → удалить ключ
        if patch[key] is None:
            if key in source:
                del source[key]

        # Если оба значения словари → рекурсия  
        elif key in source and isinstance(source[key], dict) and isinstance(patch[key], dict):
            apply_patch(source[key], patch[key])

        # Иначе → заменить или добавить
        else:
            source[key] = patch[key]

    return source


# Читаем вход
source = json.loads(sys.stdin.readline())
patch = json.loads(sys.stdin.readline())

# Применяем патч
result = apply_patch(source, patch)

# Вывод
print(json.dumps(result, separators=(',', ':'), sort_keys=True))
