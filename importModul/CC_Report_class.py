import sys, re, json, os
sys.path.append('C:/project/konservatory/data/')
sys.path.append('C:/project/konservatory/importModul/')

from DB_class import DB
import write_class
from excel_class import Excel
from importModul.get import getContent
from datetime import datetime as dt

class CC_Report(getContent):

    rowNumReport, colNumReport = 0, 0
    rowDateReport, colDateReport = 0, 0
    columName = 0
    number_СС_Report = 0
    note = 0

    gap = '#^~'

    def __init__(self, link, nameDB, globalLink, Sheet):
        getContent.__init__(self, link, nameDB, globalLink, Sheet)
        self.getNumberAndDate()
        self.replacement = {
            '\n':' ','. ':'.', 'ао«дока':'ао «дока', 'cк дока':'ск'+self.gap+'дока', '«':'', '»':'','ск ':'','-центр':'','-инжиниринг':'', 'художественно-реставрационная группа ':'','нв билдинг':'нв'+self.gap+'билдинг','ук арт-глас':'арт-глас','"':'','новое время':'новое'+self.gap+'время','политех строй':'политехстрой', 'лепной двор':'лепной'+self.gap+'двор','ван строй':'ванстрой','метеор лифт':'метеор'+self.gap+'лифт'
        }
        self.end = self.getEndData()

    def getNumberAndDate(self):
        List = [
            [r'^ОТЧЁТ №\d+ ',['colNumReport', 'rowNumReport']],         # Координаты ячейки с номером и датой отчёта
            [r'за период с',['colDateReport', 'rowDateReport']],        # Координаты ячейки с датоами начала и окончания периода отчёта
            [r'к освидетельствованию',['columnName']],                  # Столбец с названием работ и материалов
            [r'^№ п/п$',['columnNumber']],                              # Столбец с номера по порядку в отчёте
            [r'^Ед.+ измер.+$',['unitOfMeasurement']],                  # Столбец с единицами измерения
            [r'^Кол.*во$',['countColumn']],                             # Столбец с количеством
            [r'^Рабочая документация:',['workingDocumentationColumn']], # Столбец с шифром проекта или запись в ЖАН
            [r'^План$',['plane']],                                      # Столбец с планированной датой предъявления работ
            [r'^Факт$',['fact']],                                       # Столбец с фактической датой предъявления
            [r'^Субподрядчик:',['contractor_sRepresentative']],         # Столбец субподрядчика
            [r'^Исполнитель:',['executor']],                            # Столбец исполнителя
            [r'^Примечания',['note']],                                  # Столбец с примечаниями
            [r'исп.докум.',['dateSED']]                                 # Столбец с датой предоставления исполнительной документации
        ]
#
#         Через цикл
#         setattr(self, 'note', 'value')
#-------------------------------------------------------------------------------------------------------------#
#         getattr(obj, name [, default]) — для доступа к атрибуту объекта.
#         hasattr(obj, name) — проверить, есть ли в obj атрибут name.
#         setattr(obj, name, value) — задать атрибут. Если атрибут не существует, он будет создан.
#         delattr(obj, name) — удалить атрибут.
#-------------------------------------------------------------------------------------------------------------#
#
        for row in self.Content:
                
            for column in self.Content[row]:
                if self.Content[row][column] == None: temp = ''
                else: temp = str(self.Content[row][column])
                for fild in List:
                    if re.search(fild[0],temp):
                        if len(fild[1]) == 2 : setattr(self, fild[1][1], row)
                        setattr(self, fild[1][0], column)
                        if fild[1][0] == 'fact': setattr(self, 'startRow', row + 2)
            if self.rowNumReport != 0 and self.rowDateReport != 0 and self.columName != 0: break
        self.numberReport = int(re.findall(r'\d+',re.findall(r'№\d+\b', self.Content[self.rowNumReport][self.colNumReport])[0])[0])
        self.dateReport = dt.strptime(re.findall(r'\d+\.\d+\.\d+', self.Content[self.rowNumReport][self.colNumReport])[0], r'%d.%m.%Y')
        listDate = re.findall(r'\d+\.\d+\.\d+', self.Content[self.rowDateReport][self.colDateReport])
        self.startReport  = dt.strptime(listDate[0], r'%d.%m.%Y')
        self.finishReport = dt.strptime(listDate[1], r'%d.%m.%Y')
        if hasattr(self, 'dateSED'):
            self.colCCEngeneer = self.dateSED + 1
        else:
            self.colCCEngeneer = self.note + 1

    def getEndData(self):
        for row in range(self.startRow,len(self.Content)):
            if self.Content[row][self.columnNumber] == 'Вне графика':
                self.border = row
                continue
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
        listString = string.split('«')
        temp = list()
        for i in listString:
            if "»" in i:
                for j in i.split('»'):
                    temp.append(j.strip())
            else: temp.append(i.strip())

        string = self.replacementStr(string.lower())
        listString = [a.replace(self.gap,' ') for a in list(string.split())]# Восстановление пробелов в названии компаний
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

    def getEngineerCC(self, name):

        if name == None: return None

        name = name.split()[0]
        id = self.db.select('people',{'where':['`l_name` = "' + name + '"'],'columns':['id']})
        return id

    def getBuildingAxes(self, string):
        result = []
        mat = r'[ ,(]\d{,2}[ ]?-?[ ]?\d{1,2}[ ]?[\\/и]{1}[ ]?[А-Я]{0,1}_?Н?[ ]?-?[ ]?[А-Я]{1}_?Н?|[ ,(]\d{,2}[ ]?-?[ ]?\d{1,2}[ ]?[\\/и]{1}[ ]?[А-Я]{0,1}_?Н?[ ]?-?[ ]?[А-Я]{1}_?Н?$|[ ,(][А-Я]{1}_?Н?[ ]?-?[ ]?[А-Я]{0,1}_?Н?[ ]?[\\/и]{1}[ ]?\d{,2}[ ]?-?[ ]?\d{1,2}|[ ,(][А-Я]{1}_?Н?[ ]?-?[ ]?[А-Я]{0,1}_?Н?[ ]?[\\/и]{1}[ ]?\d{,2}[ ]?-?[ ]?\d{1,2}$'
        
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
            result.append(lst.replace('и','/').replace(' ',''))
        return result

    def sortAxes(self, lst: list): # Сортировка осей, приведение к общему стандарту.
        result = list()
        if not any(c.isdigit() for c in lst[0]):    # Опредиляем первую пару на наличие цифры в ней
            lst[0], lst[1] = lst[1], lst[0]             # Перестановка в случае если нервая пара не содержит цифру
        for step in lst:
            slst = step.split('-')
            if len(slst) > 1:
                if slst[0] > slst[1]:
                    slst[0], slst[1] = slst[1], slst[0]
                result.append(slst[0]+'-'+slst[1])
            else:result.append(slst[0])
        return result