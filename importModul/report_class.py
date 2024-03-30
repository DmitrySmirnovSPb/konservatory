import sys
sys.path.append('C:/project/konservatory/importModul/')

from DB_class import DB

class Report(object):

    filds = [
        'number',                           # Номер отчёта
        'date',                             # Дата отчёта
        'date_start',                       # Дата начала отчётного периода
        'date_finish',                      # Дата окончания отчётного периода
        'on_schedule',                      # Количеcтво по графику
        'off_schedule',                     # Количеcтво вне графика
        'not_presented',                    # Количеcтво не предъявленых
        'not_accepted_for_various_reasons', # Количеcтво не принятых по различным причинам
        'accepted_in_the_previous_period',  # Количеcтво принятых в предыдущий период
        'accepted'                          # Количеcтво принятых
    ]

    def __init__(self, data: dict):
        self.data = dict()
        self.error = list()
        for fild in self.filds:
            try:
                self.data[fild] = data[fild]
            except:
                self.data[fild] = None
                self.error.append(fild)
                
        self.db = DB()
        self.table = 'report'

    def checkingTheRecord(self):            # Проверка на наличее записи в базе данных воврвщает ID или False
        
        id = self.db.select(self.table, {'where':['`date` = "%s"'%self.data['date']],'columns':['id']})
        if id != None: return id
        return False

    def delError(self, key):
        try:
            self.error.remove(key)
        except:
            print('Не удалось удалить ошибку %s.'%key)

    def makingAnEntry(self):                # Занесение записи в базу данных
        if len(self.error) != 0:
            return False
        id = False
        try:
            id = self.db.insert(self.table, [list(self.data.keys()),[list(self.data.values())]])
            print(id)
        except:
            print('mysql.connector.errors.IntegrityError')
        return id
    
    def update(self, id:int):               # Изменение записи с ID = id в базе данных

        dataUpdate = dict()

        for key in self.data:
            if self.data[key] == None:
                continue
            dataUpdate[key] = self.data[key]

        id = self.db.update(self.table,{'where':['`id` = %s '%id],'data':dataUpdate})

    def getFields(self, lst):               # Получить поле или поля при наличии или None если поля нет bkb lfyyst yt rjhhtrnys
        if type(lst) == str:
            try:
                return getattr(self, lst)
            except:
                return None
        elif type(lst) == list:
            result = dict()
            for key in lst:
                try:
                    result[key] = getattr(self, key)
                except:
                    pass
            return result if len(result) > 0 else None
        else:
            return None