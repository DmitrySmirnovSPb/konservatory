import sys, re, json, os
sys.path.append('C:/project/konservatory/data/')
sys.path.append('C:/project/konservatory/importModul/')

from DB_class import DB
import write_class
from excel_class import Excel

class getContent(object):

    CONST_YEAR = 2014
    CONST_LIST_TAB = ['chapter','estimate_number','notes','justification','name_of_works_and_materials','contractor','dimension']
    CONST_KEYS = [
        'id',
        'chapter_id',
        'number_in_order',
        'estimate_id',
        'estimate_number',
        'justification_id',
        'Year',
        'notes',
        'grey',
        'name_id',
        'contractor_id',
        'dimension',
        'value',
        'cost',
        'tbas',
        'wpi',
        'executive_documentation'
    ]

    def __init__(self, link = '/data/предвар.xlsx', nameDB = 'polytechstroy', globalLink = False, Sheet = 'Лист1'):
        self.db = DB(nameDB)
        self.Sheet = Sheet
        if globalLink == False:
            self.globalLink = os.getcwd()
        else:
            self.globalLink = globalLink
        self.Content = self.getCont(link)
        self.match = r'Раздел \d+\. '

    # Получть ID по названию раздела
    def getChapterID(self, i):
        where = '`name` = "' + re.sub(self.match, '', self.db.escapingQuotes(i) , flags=re.I) + '"'
        result = self.db.select('chapter',{'columns':['id'],'where':[where]})
        return result if result != False else False

    # Опредиление максимального количество строк
    # self.ExcelObj.maxRow

    # Загрузка всего контента с 1 листа Excel файла в переменную
    def getCont(self, link: str):
        # Получаем текущую дерикторию нахождения файла
        self.globalLink = self.globalLink + link
        # Получаем объект класса Excel
        self.ExcelObj = Excel(self.globalLink)
        # Инициируем нужный нам лист (self.Sheet) если лист не найден, инициируется первыйлист
        Sheets = self.ExcelObj.getSheets()
        if self.Sheet in Sheets:
            index = Sheets.index(self.Sheet)
        else:
            index = 0
            print('\n*+====================================================================================+')
            print('Лист "'+str(self.Sheet)+'" в файле "'+str(link)+'" не найден!')
            print('Основным листом назначен: "'+str(Sheets[index])+'"')
        self.ExcelObj.initSheet(Sheets[index])
        # Получаем все данные с листа записанные в формате словаря
        return self.ExcelObj.getContent()

    # Получить данные из ячейки с номером и названием раздела
    # Состав входного списка list
    # data[0] - название таблицы в БД
    # data[1] - list перечня столбцов таблицы для заполнения
    # data[2] - list данных для заполнения таблицы

    def getData(self, data: list):
        temp = list()
        if data[0] == 'dimension' or data[0] == 'chapter':
            tempAr = list(data[3])
            for text in tempAr:
                if data[0] == 'chapter':
                    num = self.getNumber(text, False)
                    text = re.sub(self.match, '', text, flags=re.I)
                else: num = getNumber(text)
                temp.append([text, num])
            return [data[1],temp]
        elif data[0] == 'contractor':
            return [data[1],self.getContractor(list(data[2]))]
        else:
            return [data[1],list(data[2])]

    def getJSONNotes(self, ar : list, row: int):
        if self.Content[row][2] == None and type(self.Content[row][3]) == str:
            where = '`note` = "' + self.db.escapingQuotes(str(self.Content[row][3])) + '"'
            temp = self.db.select('notes',{'columns':['id'],'where':[where]})
            row += 1
            ar.append(temp)
            return self.getJSONNotes(ar, row)
        else: return {'row':row,'list':json.dumps(ar)}

    # Получить из строки первые цифры, если цифр нет, то вращает 1.1 Если flag = True - считается только с начала строки
    def getNumber(self, data: str, flag = True):
        match = r'\d{1,4}'
        if flag: match = '^' + match
        temp = re.findall(match, data)
        if temp == []: return 1
        return int(temp[0])

    # Получить даннные для записи в БД из файла с подрядчиками
    def getContractor(self, contractorList: list):
        tempList = []
        ws = write_class.Write(self.globalLink + '/data/contractor.txt')
        data = ws.getDictionary(';')
        for temp in contractorList:
            if temp in data:
                tempList.append([temp,data[temp]])
        return tempList

    # Определяется ли цвет шрифта в строке row (FF7F7F7F)
    def isGrey(self, row:int):
        for i in self.Content[row]:
            if self.Content[row][i] != None:
                if '7F7F7F' in str(self.ExcelObj.getFontColorCell(row, i)).upper(): return 1
                else: return 0
    # Определяет формат числа в ячейке и возвращает число в формате JSON
    def getContentCellFormatNumber(self, r: int, c: int):
        formatNum = self.ExcelObj.getCellFormatNumber(r, c)
        value = self.ExcelObj.getCell(r,c)
        valStr = str(value)
        if type(value) == float:
            if (formatNum == '0.00' and int(value*10) == value*10) or (formatNum == '0.000' and int(value*10) == value*10):
                valStr += '0'
            elif formatNum == '0.000' and int(value*100) == value*100:
                valStr += '00'
        elif type(value) == int: return json.dumps({1:str(value)})
        lst = valStr.split('.')
        result = dict()
        i = 1
        for num in lst:
            result[i] = str(num)
            i += 1
        return json.dumps(result)

    # Перезаписать записи в таблицу DB
    def addAnEntryToDB(self, data: list):
        nameTable = data[0]
        result = False
        if nameTable in self.CONST_LIST_TAB:
            select.db.clearTable(nameTable)
            result = self.db.insert(nameTable, getData(data))
        return result

    def getLS(self, string: str, match: list or str):
        if type(match) == str: return re.sub(match, '', string,flags=re.I)
        else:
            result = string
            for m in match:
                result = self.getLS(result, m)
        return result
    
    def getSelect(self, table: str, date: str):
        ListColumns = {
            'chapter':['name',self.match],
            'estimate_number':['estimate',[r'ЛС ',r' Поз(.)*']],
            'notes':['note',None],
            'justification':['position', None],
            'name_of_works_and_materials':['name', None],
            'contractor':['name',None],
            'dimension':['name',None]
        }
        whereTemp = self.db.escapingQuotes(date if ListColumns[table][1] == None else self.getLS(date, ListColumns[table][1]))
        where = '`'+ListColumns[table][0]+'` = "' + whereTemp + '"'
        result = self.db.select(table, {'where':[where], 'columns':['id']})
        if result != None: return result
        return self.db.insert(table, [[ListColumns[table][0]],[whereTemp]])
    
    def getDataDB(self, table, row, column):
        if column == 11 or column == 8: temp = self.Content[row][column]
        else: temp = str(self.Content[row][column]) if self.Content[row][column] != None else ''
        if table == 'grey': return self.isGrey(row)
        elif table == 'number_in_order': return self.getContentCellFormatNumber(row,1)
        elif table == '': return temp
        return self.getSelect(table, temp)

    # Добавить пробел между цифрой и буквой если этого пробела нет
    def addSpaceNumber(self, string: str):
        test = '0123456789'
        l = ',.'
        result = ''
        for i in range(len(string)-1):
            if string[i] in test and string[i+1] != ' ' and (string[i+1] not in test or string[i+1] not in l):
                result += string[i]+' '
            else: result += string[i]
        return result + string[endString]