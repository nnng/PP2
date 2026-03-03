print("=== ENUMERATE / ZIP EXAMPLES ===\n")

names = ["Alice", "Bob", "Charlie"]
scores = [85, 92, 78]


# ---------- 1. enumerate() ----------
print("Список с индексами:")

for index, name in enumerate(names):
    print(f"Индекс {index}: {name}")


# ---------- 2. zip() ----------
print("\nОбъединение двух списков:")

for name, score in zip(names, scores):
    print(f"{name} получил {score} баллов")


# ---------- 3. enumerate() + zip() вместе ----------
print("\nНумерованный список результатов:")

for index, (name, score) in enumerate(zip(names, scores), start=1):
    print(f"{index}. {name} — {score} баллов")