import json, time, re, datetime
from DB_class import DB

class SRTDB(object):

    data = {}

    def __init__(self, nameTable: str):
        self.nameTable = nameTable
        self.listfields = self.getFields()
        self.checkAndWriteToTheDB()
        # for field in self.listfields:
        #     print(field)

    def setFields(self, dictFields):
        error = []
        for field in dictFields:
            if field in self.listfields:
                self.data[field] = dictFields[field]
            else:
                error.append(field)
        return error
    # Инициация полученных данных, валидация
    def dataInitiation(self, dictFields):
        self.setFields(dictFields)

        if 'result' in self.data:
            self.getResult()

        self.getAMan()

    def checkAndWriteToTheDB(self):
        pass

    # Запись в data результата приёмки и правка примечаний
    def getResult(self):
        lst = { 2 : 'Не принято', 3 : 'Не предъявлено', 4 : 'Принято в предыдущий период'}
        result = 1
        if self.data['result'] != None and type(self.data['result']) != datetime.datetime:
            for key, value in lst.items():
                if value in self.data['result']:
                    result = key
                    reg = r'%s\.?\s*'%value
                    self.data['note'] = re.sub(reg,'', str(self.data['note']))
                    break
        self.data['result'] = result

    # Получить список ID людей и компаний    
    def getAMan(self):
        lst = ['id_contractor', 'id_actual_contractor', 'id_CC_engineer']
        gap = '-@#$-'
        replacement = {
            'ао«дока':'ао дока', '«':'', '»':'','\n':' ', 'cк дока':'ск'+gap+'дока', 'ск ':'','-центр':'', '-инжиниринг':'', 'художественно-реставрационная группа ':'','нв билдинг':'нв'+gap+'билдинг','ук арт-глас':'арт-глас','"':'','новое время':'новое'+gap+'время','политех строй':'политехстрой', 'лепной двор':'лепной'+gap+'двор','ван строй':'ван'+gap+'строй','метеор лифт':'метеор'+gap+'лифт', 'янтарная прядь-паркет': 'янтарная'+gap+'прядь-паркет', 'пгс систем':'пгс'+gap+'систем', 'гранит тех':'гранит'+gap+'тех'
        }
        db = DB()

        for k in lst:
            if self.data[k] != None:
                temp = self.data[k].strip().lower()

                if k == 'id_CC_engineer':
                    temp = temp.split()[0]
                    self.data[k] = db.select('people', {'columns':['id'], 'where': [' LOWER(`l_name`) = "' + temp + '"']})
                else:
                    for key, value in replacement.items():
                        temp = temp.replace(key, value)
                    temp = temp.split()
                    self.data[k] = db.select('people', {'columns':['id'], 'where': [' LOWER(`l_name`) = "' + temp[2] + '"']})
                    key = k + '_company'
                    self.data[key] = db.select('contractor', {'columns':['id'], 'where': [' LOWER(`name`) = "' + temp[1].replace(gap, ' ') + '"']})
        del db

    # Получить список полей
    def getFields(self):
        db = DB()
        lst = []
        for name in db.getListColumns(self.nameTable):
            lst.append(name[0])
        del db
        return lst