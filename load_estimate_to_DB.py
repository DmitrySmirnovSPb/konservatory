import sys, os, json, time
sys.path.append(os.getcwd() + '/')

from importModul.get import getContent

if __name__ == '__main__':

    start_time = time.time()

    gc = getContent()
    gc.db.clearTable('basic_estimate')
    chapter_id = 0
    notes = ''
    indNotes = 0
    year = gc.CONST_YEAR

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
        # Пропускаем шапку смены. Тело начинается со строки 3
        if row < 3: continue
        # Пропуск строки в примечаниях
        if indNotes > row: continue
        # Пропускаем строки из стоп списка
        if stopList.count(gc.Content[row][5]) > 0: continue
        # Получаем id раздела
        elif 'Раздел' in str(gc.Content[row][1]):
            year = gc.CONST_YEAR
            notes = ''
            chapter_id = gc.getChapterID(gc.Content[row][1])
            continue
        # Фиксируем год к которму оносится строки сметы
        elif 'года' in str(gc.Content[row][3]):
            year = gc.getNumber(gc.Content[row][3])
            continue
        # Фиксируем примечания к строкам сметы
        elif indNotes < row and type(gc.Content[row][3]) == str and gc.Content[row][2] == None:
            Notes = gc.getJSONNotes([],row)
            indNotes = Notes ['row']
            notes = Notes['list']
            continue
        # Фиксируем строки сметы в DB
        elif gc.Content[row][1] != None or gc.Content[row][2] != None:
            tempContent = dict()
            if type(gc.Content[row][1]) == int : notes, tbasWpi = '',False
            else: tbasWpi = True
            tempContent['chapter_id'] = chapter_id
            tempContent['number_in_order'] = gc.getContentCellFormatNumber(row,1)
            if gc.Content[row][2] == None: textTemp = ''
            else: textTemp = str(gc.Content[row][2])
            where = '`estimate` = "' + gc.db.escapingQuotes(gc.getLS(textTemp, [r'ЛС ',r' Поз(.)*'])) + '"'
            tempContent['estimate_id'] = gc.db.select('estimate_number',{'columns':['id'],'where':[where]})[0]
            tempContent['estimate_number'] = gc.Content[row][3]
            getWhere = gc.db.escapingQuotes(str(gc.Content[row][4]))
            if type(getWhere) == str: getWhere = '"'+getWhere+'"'
            elif getWhere == None: getWhere = '""'
            where = '`position` = ' + str(getWhere)
            tempContent['justification_id'] = gc.db.select('justification',{'columns':['id'],'where':[where]})[0]
            tempContent['Year'] = year
            tempContent['notes'] = notes
            tempContent['grey'] = gc.isGrey(row, 1)
            tempName = 'Нет названия' if gc.Content[row][5] == None else str(gc.Content[row][5])
            where = '`name` = "' + gc.db.escapingQuotes(tempName) + '"'
            tempContent['name_id'] = gc.db.select('name_of_works_and_materials',{'columns':['id'],'where':[where]})[0]
            tempContent['contractor_id'] = None if gc.Content[row][6] == None else gc.db.select('contractor',{'columns':['id'],'where':['`name` = "' + gc.db.escapingQuotes(str(gc.Content[row][6])) + '"']})[0]
            tempContent['dimension'] = None if gc.Content[row][7] == None else gc.db.select('dimension',{'columns':['id'],'where':['`name` = "' + gc.db.escapingQuotes(str(gc.Content[row][7])) + '"']})[0]
            tempContent['value'] = gc.Content[row][8]
            tempContent['cost'] = gc.Content[row][11]
            tempContent['tbas'] = tbasWpi
            tempContent['wpi'] = tbasWpi
            tempContent['executive_documentation'] = None
            print(row,'=>',gc.db.insert('basic_estimate',[list(tempContent.keys()),[list(tempContent.values())]]))
            
    # Время выполнения скрипта
    print("--- %s seconds ---" %(time.time() - start_time))