import json, time, re, datetime
from DB_class import DB

class SRTDB(object):

    data = {}

    counter = 0

    axesMatList = [
        r'[А-Яа-яABCEHKMOPTX]_?Н?\s?-\s?[А-Яа-яABCEHKMOPTX]_?Н?\s?[/и\ ]\s?\d{1,2}\s?-\s?\d{1,2}',
        r'[А-Яа-яABCEHKMOPTX]_?Н?\s?-\s?[А-Яа-яABCEHKMOPTX]_?Н?\s?[\\/и]\s?\d{1,2}',
        r'[А-Яа-яABCEHKMOPTX]_?Н?\s?[\\/и]\s?\d{1,2}\s?-\s?\d{1,2}',
        r'[А-Яа-яABCEHKMOPTX]_?Н?\s?[\\/и]\s?\d{1,2}',
        r'\d{1,2}\s?-\s?\d{1,2}\s?[\\/и]\s?[А-Яа-яABCEHKMOPTX]_?Н?\s?-\s?[А-Яа-яABCEHKMOPTX]_?Н?',
        r'\d{1,2}\s?[\\/и]\s?[А-Яа-яABCEHKMOPTX]_?Н?\s?-\s?[А-Яа-яABCEHKMOPTX]_?Н?',
        r'\d{1,2}\s?-\s?\d{1,2}\s?[\\/и]\s?[А-Яа-яABCEHKMOPTX]_?Н?',
        r'\d{1,2}\s?[\\/и]\s?[А-Яа-яABCEHKMOPTX]_?Н?'
    ]
    
    axesMat =  r'[\s,(]\d{,2}\s?-?\s?\d{1,2}\s?[\\/и]\s?[А-Яа-яA-Z]+[_\/]?Н?\s?-?\s?[А-Яа-яA-Z]?[_\/]?Н?|[ ,(]\d{,2}\s?-?\s?\d{1,2}\s?[\\/и]\s?[А-Яа-яA-Z]?[_\/]?Н?\s?-?\s?[А-Яа-яA-Z][_\/]?Н?$|[ ,(][А-Яа-яA-Z]{1}[_\/]?Н?\s?-?\s?[А-Яа-яA-Z]{0,1}[_\/]?Н?\s?[\\/и]\s?\d{,2}\s?-?\s?\d{1,2}|[ ,(][А-Яа-яA-Z]{1}[_\/]?Н?\s?-?\s?[А-Яа-яA-Z]{0,1}[_\/]?Н?\s?[\\/и]\s?\d{,2}\s?-?\s?\d{1,2}$'

    def __init__(self, nameTable : str, db: DB):
        self.db = db
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

        if 'actual_date' in self.data and type(self.data['actual_date']) == str:
            self.data['actual_date'] = None
        if 'result' in self.data:
            self.getResult()
        if 'dimension' in self.data:
            self.getDimension()
        self.processTheNameColumn()
        self.getAMan()
        self.getCode()
        # self.printField()

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
        temp = re.sub(r'[МM][_/\][HН]','М_Н',str(self.temp)).replace('по оси','/')
        tempLst = []
        for mat in self.axesMatList:
            tmp = self.clearList(re.findall(mat, temp))
            if len(tmp) > 0:
                for i in tmp:
                    tempLst.append(i)
        result = self.clearAxes(tempLst)
        # temp = self.clearList(re.findall(self.axesMat, temp))
        if len(result) == 0:
            SRTDB.counter += 1
            if self.counter > 1700 and self.counter <= 2200:
                print(self.counter, self.temp)
        # if len(temp) > 0:
        #     for f in temp:
        #         result.append(re.sub(r'[,(]','', str(f)))
        if len(result) > 0:
            temp = []
            for i in result:
                temp.append(self.sortAxes(i.split('/')))
        dlt = [self.axesMat, 'в/о', 'в осях', r',{2,}', r'\s[.;]', 'между осями']
        for mat in dlt:
            self.temp = re.sub(mat,'', self.temp)
        self.temp = self.removeDubleSpaces(self.temp)
        return temp

    def clearAxes(self, lst: list):
        if type(lst) != list or len(lst) < 2:
            return lst
        result = []
        for i in lst:
            if len(result) == 0:
                result.append(i)
            else:
                flag = False
                for j in result:
                    if i in j :
                        flag = True
                        break
                    elif j in i:
                        result.remove(j)
                        result.append(i)
                        flag = True
                        break
                if not flag:
                    result.append(i)
                    
        return result

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
                try:
                    boolean = slst[0] > slst[1]
                except Exception as e:
                    print('\n\t\t\tERROR!\n',e,'\n\n')
                    self.printField()
                    exit(1)
                if boolean:
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
        result = {'code':None,'journal':None}
        end = self.data['code']
        t = r'\b001[-/_]12-[КK]-[А-ЯA-Z]+[\. ]*[А-ЯA-Z]*\d*\.*[А-ЯA-Z]*\d*[-\.]?[А-ЯA-Z0-9]*[-\.,]?[А-ЯA-Z0-9]*[-\.,]?[А-ЯA-Z0-9]*\b'
        t1 = r'№\s?\d+\s*ЖАН\b|\bЖАН\s*№?\s*\d*\b'
        # print(end)
        if end != None:
            pr = re.findall(t, end)
            pr1 = re.findall(t1, end)

            listReplace = {
                ' ':'','-АР.1.2':'-АР1.2','КЖО':'КЖ0','A':'А','P':'Р','M':'М','H':'Н','X':'Х','E':'Е','T':'Т','K':'К','C':'С','B':'В', '№':''
            }
            if pr != []:
                result['code'] = pr[0]
                end = end.replace(pr[0], '')
                for retl in listReplace:
                    result['code'] = result['code'].replace(retl, listReplace[retl])
            if pr1 != [] and len(pr1) == 1:
                result['journal'] = self.removeDubleSpaces(pr1[0].replace('№', ''))
                try:
                    end = end.replace(result['journal'], '')
                except Exception as e:
                    print(result['journal'])
                    self.printField()
            elif len(pr1) > 1:
                result['journal'] = []
                for x in pr1:
                    end = end.replace(x, '')
                    result['journal'].append(self.removeDubleSpaces(x.replace('№', '')))
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

        for x in COP:
            where = '`code` = "'+ x +'"'
            try:
                id = self.db.select('code',{'where':[where],'columns':['id']})
            except Exception as e:
                print('\t\tERROR!!!', e)

            if id == None:
                Values =[x]
                Keys = ['code']

                if type(temp['date']) == list:
                    Values.append(temp['date'][0])
                    Keys.append('date')
                if type(temp['sheet']) == list:
                    Values.append(temp['sheet'][0])
                    Keys.append('sheet')

                try:
                    id = self.db.insert('code',[Keys,[Values]])
                except Exception as e:
                    print('\t\tERROR!!!', e)

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
        listMat = [r'([+-]\d+[.,]\d{1,3})', r'[на]{,2}\s(\d?,?\s*)+?эт\.?[аже]{,3}', r'на отм\.', r'отм\.', r'\s+[,.]', r'\bнад\s\d\sэт[.ажом]{1,4}', r'\sнад\sподвалом', r'(\s[сотпд]{,2}\s*([+-]\d+[.,]\d{1,3}))?', r'\bподвал\b', r'\bс\s+до\b', '\bнадом\b']

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
                    if len(tempF) > 0 :
                        tempFloor['floor'].append(int(tempF[0]))
                    else:
                        continue
            temp = json.loads(self.data['room'])
            if len(tempFloor) == 0 and len(temp) > 0:
                tempFloor['floor'] = int(temp[0].split('.')[0])
        # print(self.temp)
        for dlt in listMat:
            self.temp = re.sub(dlt, '', self.temp)
        self.temp = self.removeDubleSpaces(self.temp)
        return json.dumps(tempFloor)

    def getNameID(self):
        pass
        # print(self.temp)

    def getDimension(self):
        if type(self.data['dimension']) != str:
            return None

        temp = self.data['dimension'].replace('\n','/').strip()
        listDimension = temp.split('/')
        try:
            id = self.db.select('dimension',{'columns':['id'], 'where':['`name` = "' + listDimension[0] + '"']})
        except Exception as e:
            print('\t\tERROR!!!', e)
        if id == None or id == False:
            match = re.search(r'\d?', temp)
            print(match[0], temp)
            multiplicity = match[0] if match and match[0] != '' else 1
            try:
                id = self.db.insert('dimension', [['name','multiplicity'],[[temp, multiplicity]]])
            except Exception as e:
                print('\t\tERROR!!!', e)
        self.data['dimension'] = id
        if len(listDimension) > 1:
            listValue = str(self.data['dimension']).split('/')
            text = ''
            if len(listValue) > 1:
                text = str(listValue) + str(listDimension)
                self.data['value'] = listValue[0]
                if len(listValue) == len(listDimension):
                    for i in range(1,len(listValue)):
                        text += listValue[i] + listDimension[i] + '; '
                    text = text[:-2]
            if self.data['note'] == None or self.data['note'] == '':
                self.data['note'] = text
            else:
                self.data['note'] = text + '\n' + str(self.data['note'])

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

        for k in lst:
            if self.data[k] != None:
                temp = self.data[k].strip().lower()

                if k == 'id_CC_engineer':
                    temp = temp.split()[0]
                    try:
                        self.data[k] = self.db.select('people', {'columns':['id'], 'where': [' LOWER(`l_name`) = "' + temp + '"']})
                    except Exception as e:
                        print('\t\tERROR!!!', e)
                else:
                    for key, value in replacement.items():
                        temp = temp.replace(key, value)
                    temp = temp.split()
                    try:
                        self.data[k] = self.db.select('people', {'columns':['id'], 'where': [' LOWER(`l_name`) = "' + temp[2] + '"']})
                    except Exception as e:
                        print('\t\tERROR!!!', e)
                    key = k + '_company'
                    try:
                        self.data[key] = self.db.select('contractor', {'columns':['id'], 'where': [' LOWER(`name`) = "' + temp[1].replace(gap, ' ') + '"']})
                    except Exception as e:
                        print('\t\tERROR!!!', e)

    # Получить список полей
    def getFields(self):
        lst = []
        try:
            listFor = self.db.getListColumns(self.nameTable)
        except Exception as e:
            print('\t\tERROR!!!', e)
        for name in listFor:
            lst.append(name[0])
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
            string = re.sub('  ', ' ', string)
            # string = string.replace('  ', ' ')
        return string.strip()