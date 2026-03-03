import os
from functools import reduce

numbers_str = ["1", "2", "3", "4", "5", "6"]

print("Исходный список:", numbers_str)


# str->int

numbers = list(map(int, numbers_str))

print("\nПосле преобразования в int:", numbers)



# el->el**2

squared = list(map(lambda x: x ** 2, numbers))

print("\nКвадраты чисел:", squared)


# only even

even_numbers = list(filter(lambda x: x % 2 == 0, numbers))

print("\nЧетные числа:", even_numbers)


# sum

total_sum = reduce(lambda a, b: a + b, numbers)

print("\nСумма всех чисел:", total_sum)


# checking types
print("\nПроверка типов:")

for item in numbers:
    if isinstance(item, int):
        print(f"{item} является int")
    else:
        print(f"{item} НЕ является int")