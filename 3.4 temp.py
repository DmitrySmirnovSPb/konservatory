from sys import getsizeof
from timeit import timeit
from copy import deepcopy

# numbers = [int(input()) for i in range(3)]
# avg = sum(numbers) // len(numbers)
# numbers = [element for element in numbers if element > avg]
# print(numbers)

zeros = [[0] * 5] * 5
print(zeros)
zeros[0][0] = 1
print(zeros)

zeros = [[0] * 5 for i in range(5)]
print(zeros)
zeros[0][0] = 1
print(zeros)

text = 'Строка символов'
codes = [ord(symbol) for symbol in text]
print(codes)

countries = {"Россия": ["русский"],
             'Украина': ["русский", 'украинский'],
             "Беларусь": ["белорусский", "русский"],
             "Бельгия": ["немецкий", "французский", "нидерландский"],
             "Вьетнам": ["вьетнамский"]}
multiple_lang = [country for (country, lang) in countries.items() if len(lang) > 1]
print(multiple_lang)

lst =  [("Россия", "Москва"),
        ("Беларусь", "Минск"),
        ("Сербия", "Белград")]

countries = {country: capital for country, capital in lst}
print(countries)

numbers = (int(input()) for i in range(5))
print(numbers)

# Создаём итератор из одного миллиона целых чисел
numbers_iter = (i for i in range(10 ** 6))
# Выводим количество байт, занятых итератором
print(f"Итератор занимает {getsizeof(numbers_iter)} байт.")
# Создаём список
numbers_list = list(range(10 ** 6))
# Выводим количество байт, занятых списком
print(f"Список занимает {getsizeof(numbers_list)} байт.")

# print(round(timeit("s = '; '.join(str(x) for x in range(10 ** 8))", number=10), 3))
# print(round(timeit("s = '; '.join([str(x) for x in list(range(10 ** 8))])", number=10), 3))

x = [el ** 2 for el in range(5)]
y = [el ** 2 for el in range(5)]
print(x == y)
print(x is y)

numbers = [1, 2, 3]
print(f"{numbers}, id = {id(numbers)}")
numbers.append(4)
print(f"{numbers}, id = {id(numbers)}")
numbers += [5]
print(f"{numbers}, id = {id(numbers)}")
numbers = numbers + [6]
print(f"{numbers}, id = {id(numbers)}")

x = [1, 2, 3]
y = x
print(x is y)
x[0] = 0
print(x)
print(y)
print(x is y)

numbers = [[1, 2, 3],
           [4, 5, 6],
           [7, 8, 9]]
numbers_copy = numbers[:]
print([numbers_copy[i] is numbers[i] for i in range(len(numbers))])

numbers = [[1, 2, 3],
           [4, 5, 6],
           [7, 8, 9]]
numbers_copy = [elem[:] for elem in numbers]
print([numbers_copy[i] is numbers[i] for i in range(len(numbers))])

numbers = [[1, 2, 3],
           [4, 5, 6],
           [7, 8, 9]]
numbers_copy = deepcopy(numbers)
print([numbers_copy[i] is numbers[i] for i in range(len(numbers))])

a,b = 1, 5

print([number ** 2 for number in range(a, b + 1)])

numbers = [1, 5, 3, 9, 1, 9, 3, 4, 1, 2]

print({number for number in numbers if (int(number**0.5)) ** 2 == number})

print(' - '.join([str(number) for number in sorted(set(numbers))]))

string = 'открытое акционерное общество'

print(''.join(word[0].upper() for word in string.split()))

rle = [('a', 2), ('b', 3), ('c', 1)]

print(''.join(char * count for char, count in rle))

from itertools import count

for value in count(0, 0.1):
    if value <= 1:
        print(round(value, 1))
    else:
        break

from itertools import cycle

max_len = 10
s = ''
for letter in cycle('ABC'):
    if len(s) < max_len:
        s += letter
    else:
        break
print(s)

from itertools import chain

values = list(chain("АБВ", "ГДЕЁ", "ЖЗИЙК"))
print(values)

left = input().split(', ')
right = input().split(', ')

print('\n'.join([f'{child_left} - {child_right}' for [child_left, child_right] in list(zip(left, right))]))