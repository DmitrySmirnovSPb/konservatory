import json, time, re, datetime
from DB_class import DB

class SRTDB(object):

    data = {}
    axesMat =  r'[\s,(]\d{,2}\s?-?\s?\d{1,2}\s?[\\/и]{1,3}\s?[А-ЯA-Z]{0,1}[_\/]?Н?\s?-?\s?[А-ЯA-Z]{1,3}[_\/]?Н?|[ ,(]\d{,2}\s?-?\s?\d{1,2}\s?[\\/и]{1,3}\s?[А-ЯA-Z]{0,1}[_\/]?Н?\s?-?\s?[А-ЯA-Z]{1}[_\/]?Н?$|[ ,(][А-ЯA-Z]{1}[_\/]?Н?\s?-?\s?[А-ЯA-Z]{0,1}[_\/]?Н?\s?[\\/и]{1,3}\s?\d{,2}\s?-?\s?\d{1,2}|[ ,(][А-ЯA-Z]{1}[_\/]?Н?\s?-?\s?[А-ЯA-Z]{0,1}[_\/]?Н?\s?[\\/и]{1,3}\s?\d{,2}\s?-?\s?\d{1,2}$'

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
        if 'dimension' in self.data:
            self.getDimension()
        self.processTheNameColumn()
        self.getAMan()
        self.getCode()
        self.printField()

    # Обработка колонки название работ и материалов
    def processTheNameColumn(self):
        self.temp = self.data['name_id']
        self.data['axes'] = json.dumps(self.getAxes())
        self.data['room'] = self.getRoom()
        self.data['floor'] = self.getFloor()
        self.data['name_id'] = self.getNameID()
        del self.temp
    
    def checkAndWriteToTheDB(self):
        pass
    
    def getAxes(self):
        result = []
        temp = self.clearList(re.findall(self.axesMat, self.temp))
        if len(temp) > 0:
            for f in temp:
                result.append(re.sub(r'[,(]','', str(f)))
        if len(result) > 0:
            temp = []
            for i in result:
                temp.append(self.sortAxes(i.split('/')))
        dlt = [self.axesMat, 'в/о', 'в осях', r',{2,}', r'\s[.;]', 'между осями']
        for mat in dlt:
            self.temp = re.sub(mat,'', self.temp)
        self.temp = self.removeDubleSpaces(self.temp)
        
        return temp

    def sortAxes(self, lst:list):
        result = []
        if len(lst) == 0:
            return lst
        if not any(c.isdigit() for c in lst[0]):        # Опредиляем первую пару на наличие цифры в ней
            lst[0], lst[1] = lst[1], lst[0]             # Перестановка в случае если нервая пара не содержит цифру
        for step in lst:
            slst = self.removeSpaces(step).split('-')
            if len(slst) > 1:
                for i in range(len(slst)):
                    slst[i] = int(slst[i]) if slst[i].isdecimal() else slst[i]
                if slst[0] > slst[1]:
                    slst[0], slst[1] = slst[1], slst[0]
                result.append(slst)
            else:result.append(slst)
        return result

    def clearList(self, lsts: list):
        result = list()
        for lst in lsts:
            result.append(lst.replace('и','/').replace('\\','/').replace('//','/'))
        return result

    def getCode(self):
        db = DB()
        result = {'code':None,'journal':None}
        end = self.data['code']
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

        db = DB()

        for x in COP:
            where = '`code` = "'+ x +'"'
            id = db.select('code',{'where':[where],'columns':['id']})

            if id == None:
                Values =[x]
                Keys = ['code']

                if type(temp['date']) == list:
                    Values.append(temp['date'][0])
                    Keys.append('date')
                if type(temp['sheet']) == list:
                    Values.append(temp['sheet'][0])
                    Keys.append('sheet')

                id = db.insert('code',[Keys,[Values]])

            tempID.append(id)

        temp['id'] = tempID
        if len(data['end']) > 0:
            temp['note'] = data['end']
        else:
            temp['note'] = None
        self.data['code'] = json.dumps(temp)

    def getRoom(self):

        mach = r'(\b\d\.\d\.\d{2}\w?)+'
        lst = re.findall(mach, self.temp)
        dltList =[mach,r'пом\.\s?,*']
        for dlt in dltList:
            self.temp = re.sub(dlt, '', self.temp)
        
        return json.dumps(lst)

    def getFloor(self):
        text = self.temp

        tempFloor = {}
        listMat = [r'([+-]\d+[.,]\d{1,3})', r'\d?\s?эт\.?', r'на отм\.', r'отм\.', r'\s?[,.]', r'\bнад\s\d\sэт[\.ажом]{1,4}', r'\b\d эт[.аж]{,2}', r'\sнад\sподвалом', r'(\s[сотпд]{,2}\s*([+-]\d+[.,]\d{1,3}))?']

        altitude_mark = re.findall(listMat[0], text)
        if len(altitude_mark) > 0:
            tempFloor['altitude_mark'] = altitude_mark
        if 'подвал' in text:
            tempFloor={'floor': [-1]}
        else:
            temp = re.findall(listMat[1], text)
            if type(temp) == list and len(temp) > 0:
                tempFloor['floor'] = []

                for fl in temp:
                    tempF = re.findall(r'\d', fl)
                    if len(tempFloor) > 0 :
                        tempFloor['floor'].append(int(tempF[0]))
                    else:
                        continue
            temp = json.loads(self.data['room'])
            if len(tempFloor) == 0 and len(temp) > 0:
                tempFloor['floor'] = int(temp[0].split('.')[0])
        print(self.temp)
        for dlt in listMat:
            self.temp = re.sub(dlt, '', self.temp)
        self.temp = self.removeDubleSpaces(self.temp)
        return json.dumps(tempFloor)

    def getNameID(self):
        print(self.temp)

    def getDimension(self):
        if type(self.data['dimension']) != str:
            return None
        db = DB()
        temp = self.data['dimension'].strip()
        id = db.select('dimension',{'columns':['id'], 'where':['`name` = "' + temp + '"']})
        if id == None or id == False:
            match = re.search(r'\d?', temp)
            multiplicity = match[0] if  match else 1
            id = db.insert('dimension',[['name','multiplicity'],[[temp, multiplicity]]])
        self.data['dimension'] = id

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

    # Получить список полей
    def getFields(self):
        db = DB()
        lst = []
        for name in db.getListColumns(self.nameTable):
            lst.append(name[0])
        del db
        return lst

    # распечатать содержимое self.data
    def printField(self):
        for field in self.data:
            print(field, '=', self.data[field])

    # Удалить все пробельные символы
    def removeSpaces(self, string:str):
        return re.sub(r'\s', '', string)

    # Удалить все двойные и более пробельные символы
    def removeDubleSpaces(self, string:str):
        while '  ' in string:
            string = string.replace('  ', ' ')
        return string.strip()