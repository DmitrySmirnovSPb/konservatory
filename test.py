import sys, os, json, time, re
sys.path.append(os.getcwd() + '/')
from importModul.CC_Report_class import CC_Report
from importModul.row_class import Row
from importModul.report_class import Report

def getRoom(text):
    if text == None:
        return False
    mach = r'(\b\d\.\d\.\d{2}\w?)+'
    lst = re.findall(mach, text)
    return json.dumps(lst)

def getFloor(text):
    result = {}
    mach_1 = r'([+-]\d+[\.,]\d{1,3})'
    result['altitude_mark'] = re.findall(mach_1, text)
    
    mach_2 = r'(\d? ?(эт\.)|(\bэтаж) \d?)'
    temp = re.findall(mach_2, text)
    if type(temp) != list or len(temp) == 0:
        return result
    
    result['floor'] = list()
    for fl in temp[0]:
        print(fl,'*******************************')
        tempFloor = re.findall(r'\d', fl)
        if len(tempFloor) > 0 :
            result['floor'].append(int(tempFloor[0][0]))
        else:
            continue
    print('*****')
    return result

if __name__ == '__main__':

    start_time = time.time()

    finalityDict = dict()

    match = r'^Отчет №\d*.*\.xlsx$'

    path = '//srv-fs-02.stroy.local/Shares/Консерватория/21. Строительный контроль/Еженедельные отчеты/2024/'

    rez = sorted(os.listdir(path))
    result = []

    for string in rez:
        temp = re.search(match, string)
        if temp:
            result.append(temp[0])
    result.sort()

    listick = ['columnNumber',          # Столбец с номера по порядку в отчёте
        'columnName',                   # Столбец с названием работ и материалов
        'call_Customer',                # Столбец с номером заявки вызова заказчика
        'number_the_Customer',          # Столбец с номером по порядку из вызова Заказчика
        'unitOfMeasurement',            # Столбец с единицами измерения
        'countColumn',                  # Столбец с количеством
        'workingDocumentationColumn',   # Столбец с шифром проекта или запись в ЖАН
        'plane',                        # Столбец с планированной датой предъявления работ
        'fact',                         # Столбец с фактической датой предъявления
        'contractor_sRepresentative',   # Столбец субподрядчика
        'executor',                     # Столбец исполнителя
        'note',                         # Столбец с примечаниями
        'dateSED',                      # Столбец с датой предоставления исполнительной документации
        'colCCEngeneer']                # Столбец с именем инженера

    for item in result:
        scheduledCall = True            # Вызов по графику
        gc = CC_Report(link = item, globalLink = path, Sheet = 'Отчёт', nameDB = 'polytechstroy')
        
        report = Report({})

        for key in report.data:
            try:
                report.data[key] = getattr(gc, key)
                report.delError(key)
            except:
                report.data[key] = None

# Запись в БД report, проверка существоания записи по дате отчёта
        idReport = report.checkingTheRecord()
        if idReport == False:
            idReport = report.makingAnEntry() 

        if idReport != False:
            if len(gc.db.anyRequest('SELECT `id` FROM `сс_accepted_volumes` WHERE `number` = %s;'%idReport)) > 0:
                continue

        flag = True
        for row in range(gc.startRow, gc.end + 1):
            print('\n+----------------------------------------------------------------------+\n')
            if gc.Content[row][gc.columnNumber] == 'Вне графика' and flag:
                flag = False
                continue
            name = gc.Content[row][gc.columnName]
            tempDict = {'number':idReport,'in_the_chart':flag}
            for key in listick:
                try:
                    tempDict[key] = gc.Content[row][getattr(gc,key)]
                except:
                    tempDict[key] = None
            tempDict['number_in_order'] = gc.Content[row][getattr(gc,'columnNumber')]

            rowClass = Row({row:tempDict})
            if row > 100:
                exit(0)
        exit(0)

    # Время выполнения скрипта
    print("--- %s секунд ---" %(time.time() - start_time))
