import json, time, re, datetime, inspect
from DB_class import DB

class SRTDB(object):

    data = {}

    dictPeople = {'id_contractor':'Представитель подрядчика', 'id_actual_contractor':'Представитель исполнителя работ', 'id_CC_engineer':'Инженер строительного контроля'}

    counter = 0
    test = True

    axesMatList = [
        r'[А-Яа-яABCEHKMOPTX]_?Н?\s?-\s?[А-Яа-яABCEHKMOPTX]_?Н?\s?[\\/_]\s?\d{1,2}\s?-\s?\d{1,2}',
        r'[А-Яа-яABCEHKMOPTX]_?Н?\s?-\s?[А-Яа-яABCEHKMOPTX]_?Н?\s?[\\/]\s?\d{1,2}',
        r'[А-Яа-яABCEHKMOPTX]_?Н?\s?[\\/_]\s?\d{1,2}\s?-\s?\d{1,2}',
        r'[А-Яа-яABCEHKMOPTX]_?Н?\s?[\\/_]\s?\d{1,2}',
        r'\d{1,2}\s?-\s?\d{1,2}\s?[\\/_]\s?[А-Яа-яABCEHKMOPTX]_?Н?\s?-\s?[А-Яа-яABCEHKMOPTX]_?Н?',
        r'\d{1,2}\s?[\\/_]\s?[А-Яа-яABCEHKMOPTX]_?Н?\s?-\s?[А-Яа-яABCEHKMOPTX]_?Н?',
        r'\d{1,2}\s?-\s?\d{1,2}\s?[\\/_]\s?[А-Яа-яABCEHKMOPTX]_?Н?',
        r'\d{1,2}\s?[\\/_]\s?[А-Яа-яABCEHKMOPTX]_?Н?'
    ]

    axesMat =  r'[\s,(]\d{,2}\s?-?\s?\d{1,2}\s?[\\/и]\s?[А-Яа-яA-Z]+[_\/]?Н?\s?-?\s?[А-Яа-яA-Z]?[_\/]?Н?|[ ,(]\d{,2}\s?-?\s?\d{1,2}\s?[\\/и]\s?[А-Яа-яA-Z]?[_\/]?Н?\s?-?\s?[А-Яа-яA-Z][_\/]?Н?$|[ ,(][А-Яа-яA-Z]{1}[_\/]?Н?\s?-?\s?[А-Яа-яA-Z]{0,1}[_\/]?Н?\s?[\\/и]\s?\d{,2}\s?-?\s?\d{1,2}|[ ,(][А-Яа-яA-Z]{1}[_\/]?Н?\s?-?\s?[А-Яа-яA-Z]{0,1}[_\/]?Н?\s?[\\/и]\s?\d{,2}\s?-?\s?\d{1,2}$'

    def __init__(self, nameTable : str, db: DB):
        self.db = db
        self.nameTable = nameTable
        self.listfields = self.getFields()
        # self.checkAndWriteToTheDB()
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
        errors = self.setFields(dictFields)

        if 'actual_date' in self.data and type(self.data['actual_date']) == str:
            self.data['actual_date'] = None
        if 'result' in self.data:
            self.getResult()
        if 'dimension' in self.data:
            self.getDimension()
        self.processTheNameColumn()
        self.getCode()
        self.checkAndWriteToTheDB()
        # exit(1)

    # Обработка колонки название работ и материалов
    def processTheNameColumn(self):
        self.temp = self.data['name_id']
        self.data['axes'] = json.dumps(self.getAxes())
        self.data['room'] = self.getRoom()
        self.data['floor'] = self.getFloor()
        self.data['name_id'] = self.getNameID()
        del self.temp

    def getWhereTocheckAndWriteToTheDB(self, data_list):
        where = []
        for key in data_list:
            if type(self.data[key]) == datetime.datetime:
                val = self.data[key].strftime('%Y-%m-%d')
                where.append(['AND',f'`{key}` = "{val}"'])
            elif type(self.data[key]) == int:
                where.append(['AND',f'`{key}` = {self.data[key]}'])
            elif type(self.data[key]) == float:
                where.append(['AND',f' `{key}` = {round(self.data[key], 2)}'])
            elif type(self.data[key]) == bool:
                if self.data[key] : val = 'TRUE'
                else: val = 'FALSE'
                where.append(['AND',f'`{key}` is {val}'])
            elif self.data[key] == None:
                where.append(['AND',f'`{key}` is NULL'])
            else:
                where.append(['AND',f"`{key}` = '{self.data[key]}'"])
        return where

    def getNumberID(self):
        date = year = self.data['actual_date'] if self.data['actual_date'] != None else self.data['date_of_the_call']
        date = datetime.datetime.strftime(date, f'%Y-%m-%d')
        id = self.db.selectCell('report', {'columns': ['id'], 'where':[['AND',f'YEAR("{date}") = YEAR(`date`)'], ['AND',f'{self.data["number"]} = `number`']]})
        if id == None:
            print('\n' + '#'*100)
            print(f'#\tСистема не нащла отчет №{self.data["number"]} за {datetime.datetime.strftime(year, r"%Y")} г.')
            print('#'*100 + '\n')
            id = self.inputReport(self.data["number"])
        if type(id) != int:
            exit('def getNumberID(self):')
        return id

    def inputReport(self, number):
        listKeys = {'date':['date','Дата создания отчёта в фомате ДД.ММ.ГГГГ'], 'date_start':['date','Дата начала отчетного периода в фомате ДД.ММ.ГГГГ'], 'date_finish':['date','Дата окончания отчётного периода в фомате ДД.ММ.ГГГГ'], 'on_schedule':['int','Количество вызовов по графику'], 'off_schedule':['int','Количество вызовов вне графика'], 'not_presented':['int','Количество не предъявленых работ по графику'], 'not_accepted_for_various_reasons':['int','Количество вызовов не принятых по различным причинам по графику'], 'accepted_in_the_previous_period':['int','Количество ранее принятых работ'], 'accepted':['int','Количество принятых работ.']}
        dataInput = {'number':number}
        for value, dataType in listKeys.items():
            temp = {'error': None}
            flag =True 
            while flag:
                if temp['error'] != None:
                    er = 48 *'!'
                    print(f'{er}\nОшибка ввода данных пожалуйста введите правильные данные!\n{temp["error"]}:')
                temp = self.chekInput(input(f'Введите {dataType[1]} тип данных {dataType[0]}: '), dataType)
                print(temp)
                flag = temp['flag']
            dataInput[value] = temp['value']
        return self.db.insert('report',[list(dataInput.keys()),[list(dataInput.values())]])

    def chekInput(self, data, dataType):
        match dataType[0]:
            case 'int':
                result = re.findall(r'\d+', data)
                if result == None or len(result) == 0:
                    return {'flag':True, 'error': 'Целое число (В фомате int)'}
                elif len(result) > 1:
                    return {'flag':True, 'error': 'Одно целое число (В фомате int)'}
                return {'flag':False, 'error': None, 'value':int(result[0])}
            case 'date':
                date  = re.findall(r'\d{2}\.\d{2}\.\d{4}', data)
                if date == None or len(date) == 0:
                    return {'flag':True, 'error': 'В фомате ДД.ММ.ГГГГ'}
                elif len(date) > 1:
                    return {'flag':True, 'error': 'Одну дату в фомате ДД.ММ.ГГГГ'}
                try:
                    datetime.datetime.strptime(date[0], f'%d.%m.%Y')
                    ld = date[0].split('.')
                    result = f'{ld[2]}-{ld[1]}-{ld[0]}'
                except Exception as e:
                    return {'flag':True, 'error': f'Не корректная дата. Введите коррекную дату.\nОшибка: {e}'}
                return {'flag':False, 'error': None, 'value':result}
            case _:
                return {'flag':True, 'error': f'Не нашли тип {dataType[0]}'}

    def checkAndWriteToTheDB(self):
        listKeys = ['in_the_chart', 'number', 'number_in_order', 'name_id']
        self.data['number'] = self.getNumberID()
        if self.data['date_of_the_call'] != None:
            listKeys.append('date_of_the_call')
        else:
            listKeys.append('actual_date')
        where = self.getWhereTocheckAndWriteToTheDB(listKeys)

        # Проверка наличие записи в БД по полям:
        #                                       - наличие в заявке вызова Заказчика
        #                                       - id отчёта
        #                                       - номер по порядку в отчёте
        #                                       - id Названия работы или материала.

        id = self.db.selectCell(self.nameTable,{'columns':['id'],'where':where})
        self.getAMan()
        # self.printField()
        # exit('class SRTDB: checkAndWriteToTheDB()')

        if id == None :                         # Если запись отсутствует, заносится новая звпись
            if self.test:
                print(self.db.selectCell(self.nameTable,{'columns':['id'],'where':where, 'test': True}))
                print('self.data[\'date_of_the_call\']',self.data['date_of_the_call'])
                print('self.data[\'actual_date\']',self.data['actual_date'])
                print('where', where)
                # exit(' def checkAndWriteToTheDB(self): не нашли в базе')
            self.bringingTheDataToTheCorrectFormat()
            id = self.db.insert(self.nameTable,[list(self.data.keys()),[list(self.data.values()),]], test = self.test)

        return id
    def bringingTheDataToTheCorrectFormat(self):
        print('\t======= def bringingTheDataToTheCorrectFormat =======')
        for key, value in self.data.items():
            if type(value) == datetime.datetime:
                self.data[key] = str(value)[:10]
            # elif type(value) == bool:
            #     self.data[key] = str(value).upper()
            # elif value == None:
            #     self.data[key] = 'NULL'
            # print('{:30}\t=>\t{}'.format(key, self.data[key]))


    def getAxes(self):
        result = []
        temp = re.sub(r'[МM]+[/\]+[HН]+','М_Н',str(self.temp.replace('_','/'))).replace('по оси','/')
        tempLst = []
        for mat in self.axesMatList:
            tmp = self.clearList(re.findall(mat, temp))
            if len(tmp) > 0:
                for i in tmp:
                    tempLst.append(i)
        result = self.clearAxes(tempLst)
        temp = []
        if len(result) == 0:
            temp = self.inputAxes()
        if len(result) > 0:
            for i in result:
                temp.append(self.sortAxes(i.split('/')))
        dlt = self.axesMatList + [r'в\s?/\s?о', 'в осях', r',{2,}', r'\s[.;,]',r'[.;,]{2,}' , 'между осями']
        for mat in dlt:
            self.temp = re.sub(mat,'', self.temp)
        self.temp = self.removeDubleSpaces(self.temp)
        return temp

    def inputAxes(self):
        print('\nВведите оси из ниже предоставленной записи в формате Ч-Ч/Б-Б, где Ч - это число от 1 до 37, Б - это буква от А до Я, включая М/Н\n\tЕсли осей несколько введите их последовательно разделяя знаком ";"')
        print(self.temp)
        inp = input('Введите значение: ')
        result = []
        if inp != '':
            inp = inp.upper()
            f = self.removeSpaces(inp).split(';')
            for i in f:
                i = re.sub(r'[МM]+/[HН]+','М_Н',i.replace('\\','/'))
                result.append(i)
        return result

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
                    print('\n\t\t\tERROR!\ndef sortAxes\n',e,f'\n{slst}\n')
                    self.printField()
                    exit("sortAxes(self, lst:list) 256")
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
                id = self.db.selectCell('code',{'where':[where],'columns':['id']})
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

        mach = r'(\b\d{1}[.,]{1}\d{1}[.,]{1}\d{2}\w?)+'
        lst = re.findall(mach, self.temp)
        dltList =[mach,r'пом\.\s?,*']
        for dlt in dltList:
            self.temp = re.sub(dlt, '', self.temp)
        result = []
        for st in lst:
            result.append(str(st).replace(',','.'))
        return json.dumps(result)

    def getFloor(self):
        text = self.temp

        tempFloor = {}
        listMat = [r'([+-]\d+[.,]\d{1,3})', r'[на]{,2}\s(\d?,?\s*)+?эт\.?[аже]{,3}', r'на отм\.', r'отм\.', r'\s+[,.]', r'\bнад\s\d\sэт[.ажом]{1,4}', r'\sнад\sподвалом', r'(\s[сотпд]{,2}\s*([+-]\d+[.,]\d{1,3}))?', r'\bподвал\b', r'\bс\s+до\b', '\bнадом\b', r'на отметке']

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
        delDict = {r'\s+:': '', r'\.{2,}':'.', r'(;\s?){2,}': ';', r'(№,\s?){1,}': '', r'(\s?;){1}': ';',r'\b"':"«", r'"\b':'»'}
        text = self.temp
        for key, val in delDict.items():
            text = re.sub(key, val, text)
        text = self.db.escapingQuotes(self.removeDubleSpaces(text))
        id = self.db.selectCell('name_of_works_and_materials', {'columns':['id'],'where':[f'`name` = "{text}"']})
        if id == None:
            if self.test:
                print(self.db.selectCell('name_of_works_and_materials', {'columns':['id'],'where':[f'`name` = "{text}"'],'test':True}))
                message = 'def getNameID(self): стока ' + str(inspect.currentframe().f_lineno)
                exit(message)
            id = self.db.insert('name_of_works_and_materials',[['name'],[[text]]])
        return id

    def getDimension(self):
        if type(self.data['dimension']) != str:
            return None

        temp = self.data['dimension'].replace('\n','/').strip()
        listDimension = temp.split('/')
        try:
            id = self.db.selectCell('dimension',{'columns':['id'], 'where':['`name` = "' + listDimension[0] + '"',]})
        except Exception as e:
            print('\t\tERROR!!!', e)
        if id == None or id == False:
            match = re.search(r'\d?', temp)
            print(match[0], temp)
            multiplicity = match[0] if match and match[0] != '' else 1
            try:
                id = self.db.insert('dimension', [['name','multiplicity'],[[temp, multiplicity]]])
            except Exception as e:
                print('getDimension -> \t\tERROR!!!', e)
        self.data['dimension'] = id
        if len(listDimension) > 1:
            listValue = str(self.data['value']).replace(',','.').split('/')
            text = ''
            if len(listValue) > 1:
                text = str(listValue) + str(listDimension)
                self.data['value'] = float(listValue[0])
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

        for k in list(self.dictPeople.keys()):
            if self.data[k] != None:
                flag = self.data[k].strip().lower()
                temp = self.replasement(flag)
                if k == 'id_CC_engineer':
                    tmp = self.replasement(flag)[0]
                else:
                    tmp = self.replasement(flag)[2]
                try:
                    self.data[k] = self.db.selectCell('people', {'columns':['id'], 'where': [' LOWER(`l_name`) = "' + tmp + '"']})
                except Exception as e:
                    print('\t\tERROR!!!', e)
                if k == 'id_CC_engineer':
                    continue
                key = k + '_company'
                if self.data[k] != None:
                    try:
                        self.data[key] = self.db.selectCell('contractor', {'columns':['id'], 'where': [' LOWER(`name`) = "' + temp[1] + '"']}) # .replace(gap, ' ')
                    except Exception as e:
                        print('\t\tERROR!!!', e)
                if self.data[key] != None:
                    continue
                tmp = self.inputPeople(k, temp)
                self.data[k] = tmp[0]
                self.data[key] = tmp[1]
                # exit('getAMan(self) -> inputPeople(self, key, text)')
        # self.printField()
        # exit("getAMan(self):")

    def inputPeople(self, key, listText):
        text = ' '.join(listText)
        print(f'self.data[\'{key}\'] == None:........', text )
        print(f'Система не нашла "{text}" в базе данных. Введите, пожалуйста, необходимые данные.\n\n * - обязательны поля для заполнения.\n')
        stepDict = {'f_name':['имя',32],
            'l_name':['фамилию *',32],
            'm_name':['отчество',32],
            'initials':['инициалы',6],
            'position':['должность',100],
            'email':['адрес элетронной почты',32],
            'phone_number':['номер телефона',20]}
        resultDict = {}

        while len(stepDict) > 0:
            stopList =[]
            for k, textInput in stepDict.items():
                resultDict[k] = input(f'Введите, пожалуйста, {textInput[0]} (не более {textInput[1]} символов): ')
                if k == 'l_name' and len(resultDict[k]) == 0 :
                    continue
                if len(resultDict[k]) <= textInput[1]:
                    stopList.append(k)
            for k in stopList:
                stepDict.pop(k)
        id_contractor = self.db.selectCell('contractor', {'columns':['id'], 'where':[f'LOWER(`name`) = "{listText[1]}"'], 'test':self.test})
        if type(id_contractor) != int:
            print(f'\nСистема не нашла "{listText[0].upper()} {listText[1].upper()}" в базе данных. Введите, пожалуйста, необходимые данные.\n\n * - обязательны поля для заполнения.\n')
            name = listText[1]
            full_name = self.db.escapingQuotes(input('Введите, пожалуйста, полное название организации * (не более 128 символов): '))
            abbreviated_name = self.db.escapingQuotes(input('Введите, пожалуйста, сокращенное название организации (не более 50 символов): '))
            id_contractor = self.db.insert('contractor',[['name','full_name','abbreviated_name'], [[name, full_name, abbreviated_name]]], test = self.test)
        resultDict['company_id'] = id_contractor
        keyList = list(resultDict.keys())
        valueList = list(resultDict.values())
        peopleID = self.db.insert('people',[keyList, [valueList]], test = self.test)
        return [peopleID, id_contractor]

    def replasement(self, text):
        gap = '-@#$-'
        replacement = {
            'ао«дока':'ао'+gap+'дока', '«':'', '»':'','\n':' ', 'cк дока':'ск'+gap+'дока', 'ск ':'','-центр':'', '-инжиниринг':'', 'художественно-реставрационная группа ':'','нв билдинг':'нв'+gap+'билдинг','ук арт-глас':'арт-глас','"':'','новое время':'новое'+gap+'время','политех строй':'политехстрой', 'лепной двор':'лепной'+gap+'двор','ван строй':'ван'+gap+'строй','метеор лифт':'метеор'+gap+'лифт', 'янтарная прядь-паркет': 'яп-паркет', 'пгс систем':'пгс'+gap+'систем', 'гранит тех':'гранит'+gap+'тех', 'дтм спб':'дтм'+gap+'спб','строй сити':'строй'+gap+'сити','еаг инжиниринг':'еаг'+gap+'инжиниринг', 'к энд р дизайн':'к'+gap+'энд'+gap+'р'+gap+'дизайн','политехстрой-сварго':'политехстрой'
        }
        text = text.strip().lower()
        for key, value in replacement.items():
            text = text.replace(key, value)
        result = []
        for step in text.split():
            result.append(step.replace(gap, ' '))
        return result

    # Получить список полей таблицы DB
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
            string = re.sub(r'\s{2}', ' ', string)
            # string = string.replace('  ', ' ')
        return string.strip()