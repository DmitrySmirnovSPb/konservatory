import sys, re, json, os
sys.path.append(os.getcwd() +'\\data\\')
sys.path.append(os.getcwd() +'\\importModul\\')

from DB_class import DB
import write_class
from excel_class import Excel
from get import getContent
from datetime import datetime as dt

class Call_Customer(getContent):

    columName = 0
    number_СС_Report = 0
    note = 0

    gap = '#^~'

    def __init__(self, link, nameDB, globalLink, Sheet):
        getContent.__init__(self, link, nameDB, globalLink, Sheet)
        self.getNumberAndDate()
        self.replacement = {
            '\n':' ','. ':'.', 'ао«дока':'ао «дока', 'cк дока':'ск'+self.gap+'дока', '«':'', '»':'','ск ':'','-центр':'', '-сварго':'','-инжиниринг':'', 'художественно-реставрационная группа ':'','нв билдинг':'нв'+self.gap+'билдинг','ук арт-глас':'арт-глас','"':'','новое время':'новое'+self.gap+'время','политех строй':'политехстрой', 'лепной двор':'лепной'+self.gap+'двор','ван строй':'ванстрой','метеор лифт':'метеор'+self.gap+'лифт', 'ип хомченко':'ип'+self.gap+'хомченко'
        }
        self.end = self.getEndData()
        self.date()

    def getNumberAndDate(self):
        List = [
            [r' период с',['colDateReport', 'rowDateReport']],          # Координаты ячейки с датами начала и окончания периода отчёта
            [r'к освидетельствованию',['columnName']],                  # Столбец с названием работ и материалов
            [r'^№ пункта сметы контракта$',['numberInBEstimate']],      # Столбец с номером пункта из сметы контракта
            [r'^№ п/п$',['columnNumber']],                              # Столбец с номера по порядку в заявке
            [r'^Ед. измер.+$',['unitOfMeasurement']],                   # Столбец с единицами измерения
            [r'^Кол.*во$',['countColumn']],                             # Столбец с количеством
            [r'^Рабочая документация:',['workingDocumentationColumn']], # Столбец с шифром проекта или запись в ЖАН
            [r'^Дата$',['plane']],                                      # Столбец с планированной датой предъявления работ
            [r'^Субподрядчик:',['contractor_sRepresentative']],         # Столбец субподрядчика
            [r'^Исполнитель:',['executor']],                            # Столбец исполнителя
            [r'^Примечания',['note']],                                  # Столбец с примечаниями

        ]

        for row in self.Content:
            if len(List) == 0:
                self.startRow = row + 1
                break
 
            for column in self.Content[row]:
                if self.Content[row][column] == None:
                    temp = ''
                else: temp = str(self.Content[row][column])
                for field in List:
                    if re.search(field[0],temp):
                        if len(field[1]) == 2 :
                            setattr(self, field[1][1], row)
                        setattr(self, field[1][0], column)
                        List.remove(field)
                        continue

    def getEndData(self):
        for row in range(self.startRow,len(self.Content)):
            if self.Content[row][self.columnNumber] == None or self.Content[row][self.columnName] == None:
                return row - 1

    def listKeysAndValues(self, exceptions = ['db', 'ExcelObj', 'Content'], pt = False):
        if pt : result = dict()
        for key in self.__dict__.keys():
            if key in exceptions: continue
            temp = getattr(self, key)
            if not pt : print(key,'-->', temp)
            else: result[key] = temp
        if pt : return result

    def replacementStr(self, string:str):
        
        for old, new in self.replacement.items():
            string = string.replace(old,new)

        return string

    def getContractor(self, string):
        if string == None: return None
        listString = string.split('«')
        temp = list()
        for i in listString:
            if "»" in i:
                for j in i.split('»'):
                    temp.append(j.strip())
            else: temp.append(i.strip())

        string = self.replacementStr(string.lower())
        listString = [a.replace(self.gap,' ') for a in list(string.split())] # Восстановление пробелов в названии компаний
        if '' in listString: listString.remove('')

        if len(listString) <= 2:
            id = 0 # id равен 0 при отсутствии фамилии и имени человека
        else:
            id = self.db.select('people',{'where':['`l_name` = "'+listString[2]+'"'],'columns':['id']})
        if id == None:
            idContr = self.db.select('contractor',{'where':['`name` = "'+listString[1]+'"'],'columns':['id']})
            if len(listString) == 3:
                id = self.db.insert('people',[['l_name','company_id'],[[listString[2].title(),idContr]]])
            else:
                id = self.db.insert('people',[['l_name','initials','company_id'],[[listString[2].title(),listString[3].title(),idContr]]])
        return id

    def getBuildingAxes(self, string):
        result = []
        if string == None:
            return result
        mat = r'[\s,(]\d{,2}\s?-?\s?\d{1,2}\s?[\\/и]{1,3}\s?[А-ЯA-Z]{0,1}[_\/]?Н?\s?-?\s?[А-ЯA-Z]{1,3}[_\/]?Н?|[ ,(]\d{,2}\s?-?\s?\d{1,2}\s?[\\/и]{1,3}\s?[А-ЯA-Z]{0,1}[_\/]?Н?\s?-?\s?[А-ЯA-Z]{1}[_\/]?Н?$|[ ,(][А-ЯA-Z]{1}[_\/]?Н?\s?-?\s?[А-ЯA-Z]{0,1}[_\/]?Н?\s?[\\/и]{1,3}\s?\d{,2}\s?-?\s?\d{1,2}|[ ,(][А-ЯA-Z]{1}[_\/]?Н?\s?-?\s?[А-ЯA-Z]{0,1}[_\/]?Н?\s?[\\/и]{1,3}\s?\d{,2}\s?-?\s?\d{1,2}$'
        
        temp = re.findall(mat, string)
        if len(temp) > 0:
            for f in temp: result.append(re.sub(r'[,(]','', str(f)))
        return result
    
    def getAxes(self, splitList):
        st = list()
        for string in self.clearList(splitList):
            st.append(self.sortAxes(string.split('/')))
        return json.dumps(st)

    def clearList(self, lsts: list):
        result = list()
        for lst in lsts:
            result.append(lst.replace('и','/').replace(' ','').replace('\\','/').replace('//','/'))
        return result

    def sortAxes(self, lst: list):                  # Сортировка осей, приведение к общему стандарту.

        result = list()
        if not any(c.isdigit() for c in lst[0]):    # Опредиляем первую пару на наличие цифры в ней
            lst[0], lst[1] = lst[1], lst[0]         # Перестановка в случае если нервая пара не содержит цифру
        for step in lst:
            slst = step.split('-')
            if len(slst) > 1:
                if slst[0] > slst[1]:
                    slst[0], slst[1] = slst[1], slst[0]
                result.append(slst[0]+'-'+slst[1])
            else:result.append(slst[0])
        return result
    
    def date(self):
        montsDict = {
            1:'янва', 2:'февр', 3:'мар', 4:'апрел', 5:'ма', 6:'июн', 7:'июл', 8:'авгу', 9:'сентяб', 10:'октяб', 11:'нояб', 12:'декаб'
        }
        match = r'\s\d+\s[а-яА-Я]*\s*по\s\d+\s[а-яА-Я]*\s*\s202\d+'
        listDate = re.findall(match, self.Content[self.rowDateReport][self.colDateReport])
        if len(listDate) > 0:
            numbers = re.findall(r'\d+',listDate[0])
            months = re.findall(r'[а-яА-Я]{3,}',listDate[0])
        else:
            return False
        st = months[0]
        fin = months[0] if len(months) < 2 else months[1]
        print(len(months), st, fin)
        for mon in range(1,13):
            if montsDict[mon] in st:
                st = mon
            if montsDict[mon] in fin:
                fin = mon
            if type(st) == int and type(fin) == int:
                break
        if len(numbers) == 3:
            year = numbers[2]
        else:
            year = numbers[1]
        self.dateStar = (('0' + numbers[0]) if len(numbers[0]) < 2 else numbers[0]) + '-' + (('0' + str(st)) if st < 10 else str(st)) + '-' + year
        self.dateFinish = (('0' + numbers[1]) if len(numbers[1]) < 2 else numbers[1]) + '-' + (('0' + str(fin)) if st < 10 else str(fin)) + '-' + year
        print(self.dateStar)
        print(self.dateFinish)