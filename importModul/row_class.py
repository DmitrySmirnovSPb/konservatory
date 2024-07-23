import sys, re, json, os, datetime
sys.path.append('C:/project/konservatory/data/')
sys.path.append('C:/project/konservatory/importModul/')
from DB_class import DB

class Row (object):

    data = {
        'number':0,                     ### ID в таблице report номер отчета
        'in_the_chart':True,            ### В графике или вне графика
        'call_Customer':None,           ### Номер в заявке вызова заказчика
        'room':'[]',                    ### Номер помещания
        'number_the_Customer':None,     ### Номер позиции в заявке на вызов заказчика
        'number_in_b_estimate':None,    ### Предпологаемый номер по порядку в смете контракта в формате JSON
        'number_in_order':None,         ### Номер в отчёте
        'name_id':None,                 ### id Названия работы или материала
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

    error = 1

    gap = '#^~'

    mat = r'[ ,(]\d{,2}[ ]?-?[ ]?\d{1,2}[ ]?[\\/и]{1}[ ]?[А-Я]{0,1}[_/]?Н?[ ]?-?[ ]?[А-Я]{1}[_/]?Н?|[ ,(]\d{,2}[ ]?-?[ ]?\d{1,2}[ ]?[\\/и]{1}[ ]?[А-Я]{0,1}[_/]?Н?[ ]?-?[ ]?[А-Я]{1}[_/]?Н?$|[ ,(][А-Я]{1}[_/]?Н?[ ]?-?[ ]?[А-Я]{0,1}[_/]?Н?[ ]?[\\/и]{1}[ ]?\d{,2}[ ]?-?[ ]?\d{1,2}|[ ,(][А-Я]{1}[_/]?Н?[ ]?-?[ ]?[А-Я]{0,1}[_/]?Н?[ ]?[\\/и]{1}[ ]?\d{,2}[ ]?-?[ ]?\d{1,2}$'

    

    def __init__(self, row: dict, db:DB, check:bool):
        self.db = db
        self.check = check
        for i in row:
            self.number_Row = i
            self.row = row[i]
        self.replacement = {
            '\n':' ','. ':'.', 'ао«дока':'ао «дока', 'cк дока':'ск'+self.gap+'дока', '«':'', '»':'','ск ':'','-центр':'','-инжиниринг':'', 'художественно-реставрационная группа ':'','нв билдинг':'нв'+self.gap+'билдинг','ук арт-глас':'арт-глас','"':'','новое время':'новое'+self.gap+'время','политех строй':'политехстрой', 'лепной двор':'лепной'+self.gap+'двор','ван строй':'ванстрой','метеор лифт':'метеор'+self.gap+'лифт', 'политехстрой-сварго':'политехстрой', 'пгс систем':'пгс'+self.gap+'систем', 'янтарная прядь-паркет':'янтарная'+self.gap+'прядь-паркет', 'гранит тех':'гранит'+self.gap+'тех'
        }
        self.get_Init_Data()
        # self.printFields()
    
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
        if self.check:
            self.checkRowToDB()
        else:
            self.setRowToDB()

    def getResult(self):
        if self.data['note'] == None:
            self.data['result'] = 1
            return
        tx = str(self.data['note']).lower()
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

        temp = re.findall(self.mat, self.row['columnName'])
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
            result.append(lst.replace('и','/').replace(' ','').replace('\\','/'))
        return result

    def sortAxes(self, lst: list): # Сортировка осей, приведение к общему стандарту.
        result = list()
        if not any(c.isdigit() for c in lst[0]):    # Опредиляем первую пару на наличие цифры в ней
            lst[0], lst[1] = lst[1], lst[0]         # Перестановка в случае если нервая пара не содержит цифру
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

        # db = DB('polytechstroy')

        for key, value in list_Dict.items():
            string = self.row[value]
            if string == None: return None

            if value == 'colCCEngeneer':
                self.data[key] = self.getEngineerCC(string)
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
                id = self.db.select('people',{'where':['`l_name` = "'+listString[2]+'"'],'columns':['id']})
            if id == None:
                idContr = self.db.select('contractor',{'where':['`name` = "'+listString[1]+'"'],'columns':['id']})
                if len(listString) == 3:
                    id = self.db.insert('people',[['l_name','company_id'],[[listString[2].title(),idContr]]])
                else:
                    print(listString, idContr)
                    print(['l_name','initials','company_id'],[[listString[2].title(),listString[3].title(),idContr]])
                    id = self.db.insert('people',[['l_name','initials','company_id'],[[listString[2].title(),listString[3].title(),idContr]]])
            self.data[key] = id

    def getEngineerCC(self, name):

        if name == None: return None

        name = name.split()[0]
        id = self.db.select('people',{'where':['`l_name` = "' + name + '"'],'columns':['id']})

        return id

    def replacementStr(self, string:str):

        for old, new in self.replacement.items():
            string = string.replace(old,new)

        return string

    def checkRowToDB(self):
        
        result = {}
        tempListColumn =self.db.selectAll('сс_accepted_volumes',{'where':['`number` = "' + str(self.data['number']) + '" AND `number_in_order` = "' + str(self.data['number_in_order']) + '" AND `name_id` = '+ str(self.data['name_id'])],'columns':['*']})[0]
        if tempListColumn == None:
            print('Ошибка! Не найдена запись: ID отчёта', self.data['number'], 'Номер строки:',self.data['number_in_order'])
            id = self.setRowToDB()
            print('В БД занесена строка с id', id)

        else:
            for column, value in zip([i[0] for i in self.db.getListColumns('сс_accepted_volumes')], tempListColumn):
                result[column] = value
            del result['id']
            for key in result:
                if result[key] != self.data[key]:
                    print(f'{key:50} было:{result[key]}, стало: {self.data[key]}')

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
            self.data['floor']=json.dumps({'floor': [-1]})
            return
        mach_2 = r'\d?\s?эт\.?.*'
        temp = re.findall(mach_2, text)
        if type(temp) == list and len(temp) > 0:
            self.data['floor']['floor'] = list()
            for fl in temp:

                tempFloor = re.findall(r'\d', fl)
                if len(tempFloor) > 0 :
                    self.data['floor']['floor'].append(int(tempFloor[0]))
                else:
                    continue
        temp = json.loads(self.data['room'])
        if len(self.data['floor']) == 0 and len(temp) > 0:
            self.data['floor']['floor'] = int(temp[0].split('.')[0])
        self.data['floor'] = json.dumps(self.data['floor'])

    def getDates(self):

        self.data['date_of_the_call'] = self.row['plane'].date() if type(self.row['plane']) == datetime.datetime else None   # Дата предъявления объёмов по графику
        try:
            self.data['actual_date'] = None if '---' in str(self.row['fact']) or self.row['fact'] == None else self.row['fact'].date()         # Фактическая дата приёмки
        except Exception as e:
            print(self.row['fact'], e)
            print(self.data["number"], self.data['number_in_order'])

    def getIDCode(self, data):
        temp = {}

        date = re.findall(r'\b\d\d\.\d\d\.\s?\d{4}г?\.?\b', data['end']) # Проверка на наличие даты в шифре прокта

        temp['date'] = []
        if date != []:
            listOut = [' ', 'г.', 'г']
            for d in date:
                data['end'] = data['end'].replace(d, '').replace('от','').strip()
                for out in listOut:
                    d = d.replace(out, '')
                if d[-1] == '.':
                    d = d[:-1]
                temp['date'].append(str(datetime.datetime.strptime(d, '%d.%m.%Y')))
        else:
            temp['date'] = None
        sheet = []

        pattern = re.compile(r'л\.\s?\b\d+[.,]?\d*(\s?[-,]?\s?\d+[.,]?\d*)*', re.I)
        tmp = []
        for match in pattern.finditer(data['end']):
            tmp += match.group().replace('л.','').split(',')
        data['end'] = pattern.sub('', data['end'])

        if len(tmp) > 0:
            for string in tmp:
                sheet.append(string)

        if sheet != []:
            temp['sheet'] = sheet
        else:
            temp['sheet'] = None

        Keys = ['code','date']

        tmp = []
        if data['code'] != None:
            codeTemp = data['code'].replace('001_12','001/12').replace('001-12','001/12')
            tmp.append(codeTemp)
        if type(data['journal']) == list:
            for d in data['journal']:
                tmp.append(d)
        elif data['journal'] != None:
            tmp.append(data['journal'])

        COP = [x for x in tmp if x != ''] # список шифров проекта или ЖАН

        tempID = []

        for x in COP:
            where = '`code` = "'+ x +'"'
            id = self.db.select('code',{'where':[where],'columns':['id']})

            if id == None:
                Values =[x]
                Keys = ['code']

                if type(temp['date']) == list:
                    Values.append(temp['date'][0])
                    Keys.append('date')
                if type(temp['sheet']) == list:
                    Values.append(temp['sheet'][0])
                    Keys.append('sheet')

                id = self.db.insert('code',[Keys,[Values]])

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
        t = r'\b001[-/_]12-[КK]-[А-ЯA-Z]+[\. ]*[А-ЯA-Z]*\d*\.*[А-ЯA-Z]*\d*[-\.]?[А-ЯA-Z0-9]*[-\.,]?[А-ЯA-Z0-9]*[-\.,]?[А-ЯA-Z0-9]*\b'
        t1 = r'\b№?\s?\d*\s*в?\s?\bЖАН\s*№?\s*\d*\b'
        # print(end)
        if end != None:
            pr = re.findall(t, end)
            pr1 = re.findall(t1, end)

            listReplace = {
                ' ':'','-АР.1.2':'-АР1.2','КЖО':'КЖ0'
            }
            if pr != []:
                result['code'] = pr[0]
                end = end.replace(pr[0], '')
                for retl in listReplace:
                    result['code'] = result['code'].replace(retl, listReplace[retl])
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
        else:
            result['end'] = ''
        self.getIDCode(result)

    def getScopeOfWork(self):

        self.data['value'] = self.row['countColumn']                                    # Количество фактически принятых работ
        self.data['dimension'] = self.getDimension(str(self.row['unitOfMeasurement']))  # ID размерности
    
    def nameID(self):

        temp = self.row['columnName'].replace('\n', ' ')

        listDeleted = ['с отм.', r'\bдо\b','на отм.','в/о','в осях',r'\bв?\s?подвале?',r'по потолку \d этажа',r'по полу \d этажа',r'\bнад\b',r'с \d по \d эт\.?',r'\d\s?эт\.*',r'пом\.\s?\d\.\d\.\d{,3}', self.mat, r'[+-]\d+[\.,]\d{1,3}']
        for x in listDeleted:
            temp = re.sub(x,'', temp)
        temp = temp.strip()
        temp = ' '.join(temp.split())
        temp = temp.replace(' ,',',').replace(' .','.').replace(',.','.').replace('.,','.')
        if temp[-1] == ',':
            temp = temp[:-1]
        
        self.data['name_id'] = self.getID('emawfr', temp)

    def getID(self, tableName: str, name: str):

        id = self.db.select(tableName,{'where':['`name` = "' + self.db.escapingQuotes(name) + '"'],'columns':['id']})

        if id == None:
            id = self.db.insert(tableName,[['name'],[[name]]])
        
        return id

    def setRowToDB(self):
        # print('Занесение строки в БД')
        listFieds = list(self.data.keys())
        listValues = list(self.data.values())
        try:
            return self.db.insert('сс_accepted_volumes',[listFieds, [listValues]])
        except Exception as e:
            print('\n',e,'\n', self.data)
            self.errorСorrection()
    
    def errorСorrection(self):
        # for key in self.data:
        #     print(f'{type(self.data[key]):30}',f'{key:12}',self.data[key])
        if '/' in self.data['value']:
            lst = self.data['value'].split('/')#.append(self.data['value'].split('/'))
            lst_res = []
            for i in lst:
                lst_res.append(float(i.replace(',','.')))
            dimension = self.db.select('dimension',{'columns':['name'],'where':['id = '+str(self.data['dimension'])]}).split('/')
            print(dimension, lst_res)
            self.data['note'] = str(lst_res[1]) + ' ' + dimension[1] + ('\n' + str(self.data['note']) if self.data['note'] != None else '')
            self.data['dimension'] = self.getDimension(dimension[0])
            self.data['value'] = float(lst_res[0])
        elif ',' in self.data['value']:
            self.data['value'] = float(self.data['value'].replace(',','.'))
        self.error += 1
        if self.error > 10 :
            print('ERROR'+str(self.error))
            exit('ERROR! The limits of attempts to process error in errorCorrection() has been exceeded.')
        self.setRowToDB()

    def getDimension(self, dim: str):
        id = self.db.select('dimension',{'where':['`name` = "' + dim.strip() + '"'],'columns':['id']})
        if id == None:
            multiplicity = re.findall(r'\b\d+\b', str(self.row['unitOfMeasurement']))
            if len(multiplicity) == 0:
                mult = 1
            else:
                mult = int(multiplicity[0])
            id = self.db.insert('dimension',[['name','multiplicity'],[[self.row['unitOfMeasurement'].strip(),mult]]])
        return id