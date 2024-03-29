import sys, re, json, os
sys.path.append('C:/project/konservatory/data/')
sys.path.append('C:/project/konservatory/importModul/')
from DB_class import DB

class Row (object):

    data = {
        'сall_Customer':None,           # Номер в заявке вызова заказчика
        'room':'[]',                    # Номер помещания
        'number_the_Customer':None,     # Номер позиции в заявке на вызов заказчика
        'number_in_b_estimate':None,    #
        'number_in_order':None,         #
        'name_id':None,                 #
        'dimension':None,               #
        'value':None,                   #
        'code':None,                    #
        'date_of_the_call':None,        # Дата предъявления объёмов по графику
        'actual_date':None,             # Фактическая дата приёмки
        'id_contractor':None,           # id подрядчика по заявке
        'id_actual_contractor':None,    # id исполнителя работ
        'id_CC_engineer':None,          # id инженера строительного контроля принимавшиего работы
        'result':False,                 #
        'axes':None,                    # Оси в которых сдаётся объём в формате JSON
        'floor':None,                   #
        'number_report':None,           # Номер в отчёте
        'date_report':None,             # Дата отчёта
        'note':None                     # Примечания к записи
    }

    gap = '#^~'

    def __init__(self, row: dict):
        for i in row:
            self.number_Row = i
            self.row = row[i]
        self.replacement = {
            '\n':' ','. ':'.', 'ао«дока':'ао «дока', 'cк дока':'ск'+self.gap+'дока', '«':'', '»':'','ск ':'','-центр':'','-инжиниринг':'', 'художественно-реставрационная группа ':'','нв билдинг':'нв'+self.gap+'билдинг','ук арт-глас':'арт-глас','"':'','новое время':'новое'+self.gap+'время','политех строй':'политехстрой', 'лепной двор':'лепной'+self.gap+'двор','ван строй':'ванстрой','метеор лифт':'метеор'+self.gap+'лифт', 'политехстрой-сварго':'политехстрой'
        }
        print('\n-------------------------------------------------')
        print(self.number_Row,'=>\n',self.row,'\n')
        self.get_Init_Data()
    
    def get_Init_Data(self):
        self.data_Transfer()
        self.getNumberCallCustomer()
        self.getBuildingAxes()
        self.getContractor()
        self.getRoom()
        print(self.data)
        exit(0)

    def data_Transfer(self):
        for key in self.data:
            try:
                self.data[key] = self.row[key]
                print(key)
            except:
                pass

    def getRoom(self):

        if self.row['columnName'] == None:
            return False
        mach = r'(\b\d\.\d\.\d{2}\w?)+'
        lst = re.findall(mach, self.row['columnName'])
        self.data['room'] = json.dumps(lst)

    def getNumberCallCustomer(self):
        try:
            self.data['call_Customer'] = self.row['сall_Customer']
        except:
            pass

    def getBuildingAxes(self):
        result = []
        if self.row['columnName'] == None:
            return result
        mat = r'[ ,(]\d{,2}[ ]?-?[ ]?\d{1,2}[ ]?[\\/и]{1}[ ]?[А-Я]{0,1}_?Н?[ ]?-?[ ]?[А-Я]{1}_?Н?|[ ,(]\d{,2}[ ]?-?[ ]?\d{1,2}[ ]?[\\/и]{1}[ ]?[А-Я]{0,1}_?Н?[ ]?-?[ ]?[А-Я]{1}_?Н?$|[ ,(][А-Я]{1}_?Н?[ ]?-?[ ]?[А-Я]{0,1}_?Н?[ ]?[\\/и]{1}[ ]?\d{,2}[ ]?-?[ ]?\d{1,2}|[ ,(][А-Я]{1}_?Н?[ ]?-?[ ]?[А-Я]{0,1}_?Н?[ ]?[\\/и]{1}[ ]?\d{,2}[ ]?-?[ ]?\d{1,2}$'
        
        temp = re.findall(mat, self.row['columnName'])
        if len(temp) > 0:
            for f in temp: result.append(re.sub(r'[,(]','', str(f)))
        
        self.data['axes'] = self.getAxes(result)

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

    def getContractor(self):
        list_Dict = {
            'id_contractor':'contractor_sRepresentative',
            'id_actual_contractor':'executor',
            'id_CC_engineer':'colCCEngeneer'
        }
        
        db = DB('polytechstroy')

        for key, value in list_Dict.items():
            string = self.row[value]
            if string == None: return None
            
            if value == 'colCCEngeneer':
                self.data[key] = self.getEngineerCC(string, db)
                break
            listString = string.split('«')
            temp = list()
            for i in listString:
                if "»" in i:
                    for j in i.split('»'):
                        temp.append(j.strip())
                else: temp.append(i.strip())

            string = self.replacementStr(string.lower())
            listString = [a.replace(self.gap,' ') for a in list(string.split())]    # Восстановление пробелов в названии компаний
            if '' in listString: listString.remove('')

            if len(listString) <= 2:
                id = 0 # id равен 0 при отсутствии фамилии и имени человека
            else:
                id = db.select('people',{'where':['`l_name` = "'+listString[2]+'"'],'columns':['id']})
            if id == None:
                idContr = db.select('contractor',{'where':['`name` = "'+listString[1]+'"'],'columns':['id']})
                if len(listString) == 3:
                    id = db.insert('people',[['l_name','company_id'],[[listString[2].title(),idContr]]])
                else:
                    id = db.insert('people',[['l_name','initials','company_id'],[[listString[2].title(),listString[3].title(),idContr]]])
            self.data[key] = id

    def getEngineerCC(self, name, db):

        if name == None: return None

        name = name.split()[0]
        id = db.select('people',{'where':['`l_name` = "' + name + '"'],'columns':['id']})

        return id

    def replacementStr(self, string:str):
        
        for old, new in self.replacement.items():
            string = string.replace(old,new)

        return string

    def get_result(self):
        return self.data
