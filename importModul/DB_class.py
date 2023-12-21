import os
from importModul.write_class import Write
from mysql.connector import connect, Error, errorcode

class DB(object):

    def __init__(self, DBName = 'polytechstroy'):
        self.DBName = DBName
        self.cur_dir = os.getcwd()
        try:
            self.mydb = connect(**self.getConfig())
        except Error as e:
            if e.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("Something is wrong with your user name or password")
            elif e.errno == errorcode.ER_BAD_DB_ERROR:
                print("Database does not exist")
            else:
                print(e)
    # Получить данные для подключения к базе
    def getConfig(self):
        f = Write(self.cur_dir + '\\data\\data.txt')
        result = f.getDictionary(';')
        result['database'] = self.DBName
        return result
    # Новая запись в таблицу nameTable
    def insert(self, nameTable:str, rowData:list):
        # Начало составления строи команды INSERT
        temp = "INSERT INTO `" + nameTable + "` ("
        count = 0
        for cellName in rowData[0]:
            temp +='`'+str(cellName) + '`, '
            count += 1
        add_employee = temp[:-2] + ') VALUES '
        data = []
        for row in rowData[1]:
            add_employee += '('
            temp =''
            if type(row) == list:
                temp = ''
                for cell in row:
                    temp += '%s, '
                    data.append(cell)
            else:
                temp += '%s, '
                data.append(row)
            add_employee += temp[:-2] + '),'

        temp = add_employee[:-1]                    # Конец составления строки команды INSERT
        data = (*data,)                             # Преобразование списка в кортеж
        cursor = self.mydb.cursor()
        cursor.execute(temp, data)
        emp_no = cursor.lastrowid
        self.mydb.commit()
        cursor.close()
        return emp_no
    def selectAll(self, nameTable:str, query: dict):
        
        keys = query.keys()
        if 'columns' in keys and query['columns'] != '*' :
            columns = query['columns']
        else: columns = ['*']
        strQuery = 'SELECT '
        if query['columns'][0] == '*': strQuery += '* '
        else:
            for i in range(len(query['columns'])):
                strQuery += '`' + query['columns'][i] + '`,'
            temp = strQuery[:-1]
            strQuery = temp + ' '
        strQuery += 'FROM `' + nameTable + '` '
        if 'join' in keys:
            strQuery += self.joinSelect(nameTable, query['join']) + ' '
        if 'where' in keys:
            strQuery += 'WHERE ' + self.where(query['where']) + ' '
        if 'order' in keys:
            strQuery += 'ORDER BY '
            for order in query['order']:
                strQuery += '`' + order + '`'
                if not query['order'][order]:
                    strQuery += ' DESC'
                strQuery += ','
            temp = strQuery[:-1]
            strQuery = temp
        print(strQuery)
        with self.mydb.cursor() as cursor:
            cursor.execute(strQuery)
            result = cursor.fetchall()
        cursor.close()
        if result == []: return (None,)
        return result
    # Сделать выборку в таблице nameTable 1 строка
    def select(self, nameTable:str, query: dict):
        return self.selectAll(nameTable, query)[0]
    # Обновить строку в таблице nameTable
    def update(self, nameTable: str, data: dict):
        query = 'UPDATE `' + nameTable + '` SET '
        for i in data:
            if i != 'where':
                query += '`' + i + '` = "' + self.escapingQuotes(str(data[i])) + '",'
        temp = query[:-1]
        query = temp
        if 'where' in data:
            query += ' WHERE ' + self.where(data['where'])

        with self.mydb.cursor() as cursor:
            cursor.execute(query)
            self.mydb.commit()
        cursor.close()
        return
    # Выполнение любого запроса    
    def anyRequest(self, request):
        cursor = self.mydb.cursor()
        cursor.execute(request)
        # print(cursor)
        cursor.close()
    # Очистка таблицы от записей и установка id = 1
    def clearTable(self, nameTable:str):
        query = 'TRUNCATE `' + nameTable + '`'
        self.anyRequest(query)

    def where(self, where: list): # продумать автоматического составления WHERE
        return where[0]
    # Возвращает строку с экранированными слэшем кавычами и обратным слэшем
    # А также с удаленными лишними пробелами
    def escapingQuotes(self, string: str):
        if string == None: return None
        elif string == False: return False
        elif string == True: return True
        elif type(string) == float or type(string) == int: return string
        temp = ' '.join(string.split())
        if string == 'None': return None
        elif string == 'False': return False
        elif string == 'True': return True
        temp1 = temp.replace('\\','\\\\')
        temp = temp1.replace("'","\\'")
        return temp.replace('"','\\"')
    # Формирует запрос JOIN
    def joinSelect(self, tn:str, data: dict):
        result = ''
        for key in data:
            result += ' JOIN `'+ key + '` ON `' + tn +'`.`'+ data[key][0] + '` = `' + key + '`.`'+ data[key][1] + '`'
        return result
    # Получить список названия таблиц DB
    def getListTables(self):
        result = list()
        cursor = self.mydb.cursor()
        cursor.execute("SHOW TABLES FROM `"+self.DBName+"`")
        for (table_name,) in cursor:
            result.append(table_name)
        return result

    def getListColumns(self, table_name: str):
        result = list()
        cursor = self.mydb.cursor()
        query = f'SHOW COLUMNS FROM `{table_name}`'
        cursor.execute(query)
        for column in cursor:
            result.append(column)
        return result

    def __del__(self):
        self.mydb.close()