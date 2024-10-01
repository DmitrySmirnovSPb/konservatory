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
                print("Что-то не так с вашим именем пользователя или паролем в базе данных.")
            elif e.errno == errorcode.ER_BAD_DB_ERROR:
                print("База данных не существует")
            else:
                print(e)

    # Выполнение любого запроса    
    def anyRequest(self, request):
        result = []
        with self.mydb.cursor() as cursor:
            cursor.execute(request)
            for movie in cursor.fetchall():
                result.append(movie)
        return result
        # cursor = self.mydb.cursor()
        # cursor.execute(request)
        # print(cursor)
        # cursor.close()

    # Очистка таблицы от записей и установка id = 1
    def clearTable(self, nameTable:str):
        try:
            query =  'DELETE FROM `' + nameTable + '` WHERE `id` > 0;'
            self.anyRequest(query)
            query =  'ALTER TABLE `' + nameTable + '` AUTO_INCREMENT = 1;'
            self.anyRequest(query)
        except Error as e:
            print('Не удалось очистить таблицу', nameTable)
            print('ERROR:\n', e)

    # Возвращает строку с экранированными слэшем кавычами и обратным слэшем
    # А также с удаленными лишними пробелами
    def escapingQuotes(self, string: str, test = False):
        if string == None: return None
        elif string == False: return False
        elif string == True: return True
        elif type(string) == float or type(string) == int: return string
        if string == 'None': return None
        elif string == 'False': return False
        elif string == 'True': return True
        temp = self.removeSpaces(string)
        temp1 = temp.replace('\\','\\\\')
        temp = temp1.replace(f'\'',f'\\\'').replace(f"\"",f"\\\"")
        if test:
            print(string,'->\n\t',temp)
        return temp

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
        if 'test' in keys:
            print(temp, data)
        cursor = self.mydb.cursor()
        cursor.execute(temp, data)
        emp_no = cursor.lastrowid
        self.mydb.commit()
        cursor.close()
        return emp_no

    def selectAll(self, nameTable:str, query: dict):

        keys = query.keys()
        columnsList = []
        temp = []

        if 'columns' in keys and query['columns'] != ['*'] :
            columns = columnsList = query['columns']
        else:
            columns = ['*']
            temp = self.selectAll('information_schema.columns',{'columns':['COLUMN_NAME'],'where':['`table_name` = "' + nameTable + '"']})
            for column in temp:
                columnsList.append(column[0])

        strQuery = 'SELECT '
        if query['columns'][0] == '*': strQuery += '* '
        else:
            for i in range(len(query['columns'])):
                strQuery += '`' + query['columns'][i] + '`,'
            temp = strQuery[:-1]
            strQuery = temp + ' '
        if nameTable == 'information_schema.columns':
            strQuery += 'FROM ' + nameTable + ' '
        else:
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
        if 'test' in keys:
            print(strQuery+'\b;')
        with self.mydb.cursor(dictionary=True) as cursor:
            cursor.execute(strQuery+';')
            temp = cursor.fetchall()
        cursor.close()

        if nameTable == 'information_schema.columns':
            result = []
            for field in temp:
                result.append(field['COLUMN_NAME'])
            return(result)
        return temp

    # Сделать выборку в таблице nameTable 1 строка
    def select(self, nameTable:str, query: dict):
        result = self.selectAll(nameTable, query)
        if result == False: return False
        if 'return' in result and result['return'] == None: return None
        if query['columns'][0] == '*':
            return result[0]
        else:
            return result[query['columns'][0]]
     # 
    def selectCell(self, nameTable:str, query: dict):
        result = self.selectAll(nameTable, query)
        if query['columns'][0] == '*':
            columnName = 'id'
        else:
            columnName = query['columns'][0]
        if result == None or result == []:
            return None
        elif result == False:
            return False
        else:
            # if 'test' in query.keys():
            #     print(query)
            #     print(f'result[0]=>{columnName}\n',result,'\n\n')
            #     # exit('exit DB -> selectCell')
            return result[0][columnName]

    # Обновить строку в таблице nameTable
    def update(self, nameTable: str, data: dict, test = False):
        query = 'UPDATE `' + nameTable + '` SET '
        for i in data['data']:
            if i != 'where':
                query += '`' + i + '` = "' + self.escapingQuotes(str(data[i])) + '",'
        temp = query[:-1]
        query = temp
        if 'where' in data:
            query += ' WHERE ' + self.where(data['where'])
        if test:
            print('Test DB.update(self, nameTable: str, data: dict, test = False):\n',query)
        with self.mydb.cursor() as cursor:
            cursor.execute(query)
            self.mydb.commit()
        cursor.close()
        return


    # WHERE список условий при пустом списке возвращает пустую строку, при 1 записи возвращает строку спервой записью
    # если несколько условий, то список состоит из списков, где 0 элемент - это AND, OR, а 1 элемент само условие
    def where(self, where: list):
        if len(where) == 1:
            return where[0]
        elif len(where) > 1:
            result = ''
            flag = True
            for step in where:
                if flag:
                    result += step[1]
                    flag = False
                else:
                    result += ' ' + step[0] + ' ' + step[1]
            return result
        else:
            return ''
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

    # Получить список полей в таблице table_name
    def getListColumns(self, table_name: str):
        result = list()
        cursor = self.mydb.cursor()
        query = f'SHOW COLUMNS FROM `{table_name}`'
        cursor.execute(query)
        for column in cursor:
            result.append(column)
        return result

    def removeSpaces(self, string: str):
        if type(string) != str:
            return string
        while '  ' in string:
            string = string.replace('  ',' ')
        return string.strip()

    def __del__(self):
        self.mydb.close()