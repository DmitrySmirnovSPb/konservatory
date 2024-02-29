from sys import stdin

# Непрерывный ввод в список
lines = []
for line in stdin:
    lines.append(line.rstrip('\n'))
print(lines)

# Альтернативный способ ввода в список readlines()
lines = stdin.readlines()
print(lines)

# Ввод в одну строку метод read()
text = stdin.read()
print([text])
print('\n+======================================================================+\n')
file_in = open("input_1.txt", encoding="UTF-8")
for line in file_in:
    print(line)
file_in.close()

# Удаление излишненго переноса в конце строки
with open("input_1.txt", encoding="UTF-8") as file_in:
    for line in file_in:
        print(line.rstrip("\n"))

# Запись всего файла в память
with open("input_1.txt", encoding="UTF-8") as file_in:
    lines = file_in.readlines()
print(lines)

# Прочитаем 10 символов файла:
with open("input_1.txt", encoding="UTF-8") as file_in:
    symbols = file_in.read(10)
print([symbols])

# Для записи данных из строковой переменной используется метод write()
with open("output_1.txt", "w", encoding="UTF-8") as file_out:
    n = file_out.write("Это первая строка\nА вот и вторая\nИ третья — последняя\n")
print(n)

# Для записи строк из списка в файл используется метод writelines()
lines = ["Это первая строка\n", "А вот и вторая\n", "И третья — последняя\n"]
with open("output_2.txt", "w", encoding="UTF-8") as file_out:
    file_out.writelines(lines)

# Функция print() может быть использована для вывода данных в файл. Для этого нужно передать ей в аргумент file файловый объект
with open("output_3.txt", "w", encoding="UTF-8") as file_out:
    print("Вывод в файл с помощью функции print()", file=file_out)

#########
#       #
# JSON  #
#       #
#########
import json

with open("data.json", encoding="UTF-8") as file_in:
    records = json.load(file_in)
print(records)

# Из примера видно, что JSON-файл был преобразован в список словарей, а каждый словарь — это запись с информацией о студенте. Для обработки стандартных объектов мы можем применить известные операции, функции и методы. Для записи изменённых данных в JSON-файл используется метод dump(). Рассмотрим некоторые важные его аргументы:

# - ensure_ascii. Имеет значение по умолчанию True, при котором все не-ASCII-символы при выводе в файл представляют собой юникод-последовательности вида \uXXXX (коды символов в таблице кодировки). Если аргумент имеет значение False, такие символы будут записаны в виде символов, а не их кодов. В примере используются русские символы, поэтому необходимо передать в аргумент значение False.
# - indent. Задаёт вид отступа для удобства чтения данных человеком. По умолчанию аргумент имеет значение None, а данные записываются в файл одной строкой. Если задать строку вместо None, то эта строка будет использоваться в качестве отступа. Если задать число больше 0, то отступ будет состоять из такого же количества пробелов.
# - sort_keys. Позволяет отсортировать ключи словаря с данными. По умолчанию имеет значение False. Для сортировки ключей необходимо передать в аргумент значение True.
with open("data.json", encoding="UTF-8") as file_in:
    records = json.load(file_in)
records[1]["group_number"] = 2

with open("data.json", "w", encoding="UTF-8") as file_out:
    json.dump(records, file_out, ensure_ascii=False, indent=2, sort_keys=True)

records = {1: "First",
           2: "Second",
           3: "Third"}
with open("output.json", "w", encoding="UTF-8") as file_out:
    json.dump(records, file_out, ensure_ascii=False, indent=2)