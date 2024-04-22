import sys, re, json, os, datetime
sys.path.append('C:/project/konservatory/data/')
sys.path.append('C:/project/konservatory/importModul/')
from DB_class import DB

class Row (object):

    data = {
        'number':0,                     ### ID в таблице report номер отчета
        'in_the_chart':True,            ### В графике или вне графика
        'call_Customer':None,           # Номер в заявке вызова заказчика
        'room':'[]',                    ### Номер помещания
        'number_the_Customer':None,     ### Номер позиции в заявке на вызов заказчика
        'number_in_b_estimate':None,    # Предпологаемый номер по порядку в смете контракта в формате JSON
        'number_in_order':None,         ### Номер в отчёте
        'name_id':None,                 # id Названия работы или материала
        'dimension':None,               ### id Единицы измерения
        'value':None,                   ### Количество фактически принятых работ
        'code':None,                    ### Шифр проекта
        'date_of_the_call':None,        ### Дата предъявления объёмов по графику
        'actual_date':None,             ### Фактическая дата приёмки
        'id_contractor':None,           ### id подрядчика по заявке
        'id_actual_contractor':None,    ### id исполнителя работ
        'id_CC_engineer':None,          ### id инженера строительного контроля принимавшиего работы
        'result':False,                 ### Результат предъявления работ:
        'axes':None,                    ### Оси в которых сдаётся объём в формате JSON
        'floor':None,                   ### Этаж и/или отметки
        'note':None                     ### Примечания к записи
    }

    gap = '#^~'

    def __init__(self, row: dict):
        for i in row:
            self.number_Row = i
            self.row = row[i]
        self.replacement = {
            '\n':' ','. ':'.', 'ао«дока':'ао «дока', 'cк дока':'ск'+self.gap+'дока', '«':'', '»':'','ск ':'','-центр':'','-инжиниринг':'', 'художественно-реставрационная группа ':'','нв билдинг':'нв'+self.gap+'билдинг','ук арт-глас':'арт-глас','"':'','новое время':'новое'+self.gap+'время','политех строй':'политехстрой', 'лепной двор':'лепной'+self.gap+'двор','ван строй':'ванстрой','метеор лифт':'метеор'+self.gap+'лифт', 'политехстрой-сварго':'политехстрой'
        }
        self.get_Init_Data()
        self.printFields()
    
    def get_Init_Data(self):
        self.data_Transfer()
        self.getNumberCallCustomer()
        self.getBuildingAxes()
        self.getContractor()
        self.getRoom()
        self.getResult()
        self.getFloor()
        self.getDates()
        self.getCode()
        self.nameID()
        self.getScopeOfWork()

    def getResult(self):
        if self.data['note'] == None:
            self.data['result'] = 1
            return
        tx = self.data['note'].lower()
        if 'не принято' in tx:
            self.data['result'] = 2
        elif 'не предъявлено' in tx:
            self.data['result'] = 3
        elif 'принято в предыдущий период' in tx:
            self.data['result'] = 4
        else:
            self.data['result'] = 1

    def data_Transfer(self):
        for key in self.data:
            try:
                self.data[key] = self.row[key]
                # print(key,'=>',self.data[key], '     ------>     ------>    data_Transfer')
            except:
                # print(key, '* NO data_Transfer *')
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
                try:
                    slst[0], slst[1] = int(slst[0]), int(slst[1])
                except:
                    pass

                if slst[0] > slst[1]:
                    slst[0], slst[1] = slst[1], slst[0]
            result.append(slst)
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

    def printFields(self):
        print('self.data =====>')
        for field in self.data:
            print(field, self.data[field])
        # exit(0)

    def getFloor(self):

        text = self.row['columnName']

        self.data['floor'] = {}

        mach_1 = r'([+-]\d+[\.,]\d{1,3})'
        altitude_mark = re.findall(mach_1, text)
        if len(altitude_mark) > 0:
            self.data['floor']['altitude_mark'] = altitude_mark
        if 'подвал' in text:
            self.data['floor']['floor'] = [-1]
            return
        mach_2 = r'\d?\s?эт\.?.*'
        temp = re.findall(mach_2, text)
        if type(temp) == list and len(temp) > 0:
            self.data['floor']['floor'] = list()
            for fl in temp:
                # print(fl)
                tempFloor = re.findall(r'\d', fl)
                if len(tempFloor) > 0 :
                    self.data['floor']['floor'].append(int(tempFloor[0]))
                else:
                    continue
        temp = json.loads(self.data['room'])
        if len(self.data['floor']) == 0 and len(temp) > 0:
            self.data['floor']['floor'] = int(temp[0].split('.')[0])

    def getDates(self):

        self.data['date_of_the_call'] = self.row['plane']   # Дата предъявления объёмов по графику
        self.data['actual_date'] = self.row['fact'] if '---' not in str(self.row['fact']) else None         # Фактическая дата приёмки

    def getIDCode(self, data):
        temp = {}

        date = re.findall (r'\d\d\.\d\d\.\d{4}',data['end']) # Проверка на наличие даты в шифре прокта
        temp['date'] = []
        if date != []:
            for d in date:
                temp['date'].append(str(datetime.datetime.strptime(d, '%d.%m.%Y')))
                data['end'] = data['end'].replace(d, '').replace('от','').strip()
        else:
            temp['date'] = None

        sheet = re.findall (r'(\bл\.?.*\d+\.?d+\b)|(\bлист\.?.*\d+\.?d+\b)',data['end']) # Поверка на наличие укзаний на лист проекта code

        if sheet != []:
            if sheet[0][0] != '':
                sheetRes = int(sheet[0][0].replace('л.',''))
                data['end'] = data['end'].replace(sheet[0][0],'')
            else:
                sheetRes = int(sheet[0][1].replace('лист.*',''))
                data['end'] = data['end'].replace(sheet[0][1])
            temp['sheet'] = sheetRes
        else:
            temp['sheet'] = None

        Keys = ['code','date']

        tmp = []
        if data['code'] != None:
            tmp.append(data['code'])
        if type(data['journal']) == list:
            for d in data['journal']:
                tmp.append(d)
        elif data['journal'] != None:
            tmp.append(data['journal'])
        print(data)
        print(tmp)
        COP = [x for x in tmp if x != ''] # список шифров проекта или ЖАН
        
        tempID = []
        db = DB('polytechstroy')

        for x in COP:
            where = '`code` = "'+ x +'"'
            id = db.select('code',{'where':[where],'columns':['id']})

            if id == None:
                Values =[x]
                Values.append(temp['date'][0])
                id = db.insert('code',[Keys,[Values]])#('dimension',[['name','multiplicity'],[[self.row['unitOfMeasurement'],mult]]])
            
            tempID.append(id)

        temp['id'] = tempID
        if len(data['end']) > 0:
            temp['note'] = data['end']
        else:
            temp['note'] = None
        self.data['code'] = json.dumps(temp)


    def getCode(self):
        result = {'code':None,'journal':None}
        end = self.row['workingDocumentationColumn']
        t = r'\b001[-/_]12-К-[А-Я]+[\. ]?\d*\.?\d*\b'
        t1 = r'\bЖАН\s*№?\s*\d+\b'
        pr = re.findall(t, end)
        pr1 = re.findall(t1, end)
        
        if pr != []:
            result['code'] = pr[0]
            end = end.replace(result['code'], '')
        if pr1 != [] and len(pr1) == 1:
            result['journal'] = pr1[0]
            end = end.replace(result['journal'], '')
        elif len(pr1) > 1:
            result['journal'] = []
            for x in pr1:
                end = end.replace(x, '')
                result['journal'].append(x)
        if len(end) > 0 and end[0] == ',':
            end = end[1:]
        
        end = end.strip()

        result['end'] = end
        
        self.getIDCode(result)

    def getScopeOfWork(self):

        self.data['value'] = self.row['countColumn']        # Количество фактически принятых работ

        db = DB('polytechstroy')
        id = db.select('dimension',{'where':['`name` = "' + str(self.row['unitOfMeasurement']) + '"'],'columns':['id']})
        if id == None:
            multiplicity = re.findall(r'\b\d+\b', self.row['unitOfMeasurement'])
            if len(multiplicity) == 0:
                mult = 1
            else:
                mult = int(multiplicity[0])
            id = db.insert('dimension',[['name','multiplicity'],[[self.row['unitOfMeasurement'],mult]]])
        self.data['dimension'] = id
    
    def nameID(self):
        print(self.row['columnName'])