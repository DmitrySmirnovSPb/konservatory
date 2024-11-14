import sys, os, json, time
sys.path.append(os.getcwd() + '/')

from importModul.get import getContent

listTmp = ['chapter_id','notes','executive_documentation','Year','tbas', 'wpi']

dataKey = {
    'contractor_id':['contractor',6],
    'dimension':['dimension',7],
    'estimate_id':['estimate_number',2],
    'justification_id':['justification',4],
    'name_id':['name_of_works_and_materials',5],
    'estimate_number':['',3],
    'value':['',8],
    'cost':['',11],
    'color':['',1],
    'number_in_order':['number_in_order',1]
}

if __name__ == '__main__':

    start_time = time.time()

    gc = getContent( Sheet = 'Смета контракта Консерватория_1')

    dataTemp = dict()
    showTables = dict()
    
    lstTable = [x[0] for x in gc.db.anyRequest('SHOW TABLES;')]
    for table in lstTable:
        showTables[table] = [x[0] for x in gc.db.anyRequest(f'SHOW COLUMNS FROM `{table}`;')]

    # print(gc.db.selectAll('people',{'columns':['*'],}))
    # exit()
    gc.db.clearTable('basic_estimate')
    dataTemp['chapter_id'] = 0
    dataTemp['notes'] = ''
    dataTemp['executive_documentation'] = None
    dataTemp['Year'] = gc.CONST_YEAR
    indNotes = 0

    stopList = [
        'Итого сумма позиций',
        'Временные здания и сооружения – 1,44%',
        'Зимнее удорожание - 1,41%',
        'Итого',
        'Расчетная стоимость единицы',
        'Всего на физобъем',
        'Стоимость единицы',
        'Всего на физобъем'
    ]

    for row in gc.Content:
        print(f'\tROW {row}')
        # Пропускаем шапку смены. Тело начинается со строки 3
        if row < 3: continue
        # Пропуск строки в примечаниях
        if indNotes > row: continue
        # Пропускаем строки из стоп списка
        if stopList.count(gc.Content[row][5]) > 0: continue
        # Получаем id раздела
        elif 'Раздел' in str(gc.Content[row][1]):
            # dataTemp['Year'] = gc.CONST_YEAR
            # dataTemp['notes'] = ''
            dataTemp['chapter_id'] = gc.getChapterID(gc.Content[row][1])
            continue
        # Фиксируем год к которму относится строки сметы
        elif 'года' in str(gc.Content[row][3]):
            dataTemp['Year'] = gc.getNumber(gc.Content[row][3])
            continue
        # Фиксируем примечания к строкам сметы
        elif indNotes < row and type(gc.Content[row][3]) == str and gc.Content[row][2] == None:
            Notes = gc.getJSONNotes([],row)
            indNotes = Notes ['row']
            dataTemp['notes'] = Notes['list']
            continue
        # Фиксируем строки сметы в DB
        elif gc.Content[row][1] != None or gc.Content[row][2] != None:
            tempContent = dict()
            if type(gc.Content[row][1]) == int:
                dataTemp['notes'] = ''
                dataTemp['tbas'], dataTemp['wpi'] = True, True
            else: dataTemp['tbas'], dataTemp['wpi'] = False, False
            for key in showTables['basic_estimate']:
                if key == 'id': continue
                if key in listTmp:
                    tempContent[key] = dataTemp[key]
                else:
                    tempContent[key] = gc.getDataDB(dataKey[key][0],row,dataKey[key][1])
            print(row,'=>',gc.db.insert('basic_estimate',[list(tempContent.keys()),[list(tempContent.values())]]))
            
    # Время выполнения скрипта
    print("--- %s seconds ---" %(time.time() - start_time))