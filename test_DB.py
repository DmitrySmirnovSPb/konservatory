#Python, как реализовать паттерн "Одиночка" при обращении к базе данных MySQL. В классе должны быть отдельные методы на выборку, в том числе с возможностью применения Join, замену, добавление и удаление строк  из таблиц. Отдельный метод для формирования WHERE и JOIN, а также экранирования кавычек и других символов

import mysql.connector

class Database:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance.connection = mysql.connector.connect(
                host = 'localhost',
                user = 'root',
                password = '12@preli@1961',
                database = 'polytechstroy'
            )
        return cls._instance

    def select(self, table, columns='*', where=None, join=None):
        cursor = self.connection.cursor()
        query = f"SELECT {columns} FROM `{table}`"
        if join:
            query += f" {join}"
        if where:
            query += f" WHERE {where}"
        cursor.execute(query)
        result = cursor.fetchall()
        return result

    def insert(self, table, data):
        cursor = self.connection.cursor()
        columns = ', '.join(data.keys())
        values = ', '.join([f"'{value}'" for value in data.values()])
        query = f"INSERT INTO `{table}` ({columns}) VALUES ({values})"
        cursor.execute(query)
        self.connection.commit()

    def update(self, table, data, where):
        cursor = self.connection.cursor()
        updates = ', '.join([f"`{key}` = '{value}'" for key, value in data.items()])
        query = f"UPDATE `{table}` SET {updates} WHERE {where}"
        cursor.execute(query)
        self.connection.commit()

    def delete(self, table, where):
        cursor = self.connection.cursor()
        query = f"DELETE FROM `{table}` WHERE {where}"
        cursor.execute(query)
        self.connection.commit()

    def build_where(self, conditions):
        where_clause = ' AND '.join([f"`{key}` = '{value}'" for key, value in conditions.items()])
        return where_clause

    def build_join(self, table, on):
        join_clause = f"JOIN {table} ON {on}"
        return join_clause

    def escape_string(self, string):
        escaped_string = mysql.connector.conversion.MySQLConverter.escape(self.connection, string)
        return escaped_string

# Пример использования:
db = Database()

# Выборка данных с таблицы
result = db.select('people', where="`id` < 10")
print(result)

# Добавление записи в таблицу
# data = {'name': 'John', 'email': 'john@example.com'}
# db.insert('users', data)

# Обновление записи в таблице
data = {'l_name': 'Калинин'}
where = "`id` = 166"
db.update('people', data, where)

# Удаление записи из таблицы
# where = "id = 1"
# db.delete('users', where)

# Формирование WHERE
conditions = {'id': '1', 'name': 'John'}
where_clause = db.build_where(conditions)
print(where_clause)

# Формирование JOIN
join_clause = db.build_join('orders', 'users.id = orders.user_id')
print(join_clause)

# Экранирование строки
string = "John's email"
escaped_string = db.escape_string(string)
print(str(escaped_string))

# Таким образом, класс Database реализует паттерн "Одиночка" и предоставляет методы для работы с базой данных MySQL, включая выборку, добавление, обновление, удаление данных, формирование условий WHERE и JOIN, а также экранирование строк.