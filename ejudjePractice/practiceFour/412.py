import json
import sys

def serialize(value):
    return json.dumps(value, separators=(',', ':'))

def deep_diff(obj1, obj2, path=""):
    differences = []

    keys = set(obj1.keys()) | set(obj2.keys())

    for key in keys:
        new_path = f"{path}.{key}" if path else key

        if key not in obj1:
            differences.append(f"{new_path} : <missing> -> {serialize(obj2[key])}")

        elif key not in obj2:
            differences.append(f"{new_path} : {serialize(obj1[key])} -> <missing>")

        else:
            val1 = obj1[key]
            val2 = obj2[key]

            if isinstance(val1, dict) and isinstance(val2, dict):
                differences.extend(deep_diff(val1, val2, new_path))
            elif val1 != val2:
                differences.append(f"{new_path} : {serialize(val1)} -> {serialize(val2)}")

    return differences


# Чтение входа
obj1 = json.loads(sys.stdin.readline())
obj2 = json.loads(sys.stdin.readline())

diffs = deep_diff(obj1, obj2)

if not diffs:
    print("No differences")
else:
    for line in sorted(diffs):
        print(line)
