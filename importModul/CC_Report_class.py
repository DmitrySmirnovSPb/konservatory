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

    def __init__(self, link, nameDB, globalLink, Sheet):
        getContent.__init__(self, link, nameDB, globalLink, Sheet)
        self.getNumberAndDate()

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
            [r'^Примечания',['note']]                                   # Столбец с примечаниями
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

    def listKeysAndValues(self, exceptions = ['db', 'ExcelObj', 'Content'], pt = False):
        if pt : result = dict()
        for key in self.__dict__.keys():
            if key in exceptions: continue
            temp = getattr(self, key)
            if not pt : print(key,'-->', temp)
            else: result[key] = temp
        if pt : return result

    def getBuildingAxes(self, string):
        result = []
        listMtch = [
            r'\d{,2}[ ]?-?[ ]?\d{1,2}[ ]?[/и\\][ ]?[а-яА-Я]?/?Н?[ ]?-?[ ]?[а-яА-Я]/?Н?',
            r'[а-яА-Я]?/?Н?[ ]?-?[ ]?[а-яА-Я]/?Н?[ ]?[/и\\][ ]?\d{,2}[ ]?-?[ ]?\d{1,2}'
        ]
        for mat in listMtch:
            temp = re.findall(mat, string)
            if len(temp) > 0:
                for f in temp: result.append(f)
        return result
        # matchStr = 
        # F = [
            # 'Производство работ по монтажу медного балкона в/о 35-37 / Я',
            # 'Производство работ по монтажу медного балкона в/о К-С/ 19-21',
            # 'Производство работ по монтажу медного балкона в/о 35/Я',
            # 'Производство работ по монтажу медного балкона в/о А-Б / 19',
            # 'Производство работ по монтажу медного балкона в/о М/Н-С / 18',
            # ]
        # return re.findall(matchStr, string)