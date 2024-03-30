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

def getFloor(obj, row):
    return 'Заглушка'

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
    result.sort(reverse = True)

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
        scheduledCall = True # Вызов по графику
        print('\n+----------------------------------------------------------------------+\n')
        gc = CC_Report(link = item, globalLink = path, Sheet = 'Отчёт', nameDB = 'polytechstroy')
        
        report = Report({})

        for key in report.data:
            try:
                report.data[key] = getattr(gc, key)
                report.delError(key)
            except:
                report.data[key] = '\n%s -> None\n'%key

# Запись в БД report, проверка существоания записи по дате отчёта
        idReport = report.checkingTheRecord()
        if idReport == False:
            idReport = report.makingAnEntry() 

        if idReport == False:
            continue

        # for test in gc.db.anyRequest('SELECT `people`.`id` AS `id`,`people`.`f_name`,`people`.`m_name`,`people`.`l_name`,`people`.`initials`,`people`.`position` AS `Должность`,`contractor`.`name` FROM `people` JOIN `contractor` ON `people`.`company_id` = `contractor`.`id` ORDER BY `id`;'):
        #     print(test)
        # exit(0)
        tempKey = str(gc.date_start.year) + '-' + str(gc.number)
        finalityDict[tempKey] = {}
        gc.listKeysAndValues()
        flag = True
        for row in range(gc.startRow, gc.end + 1):
            name = gc.Content[row][gc.columnName]
            if gc.Content[row][gc.columnNumber] == 'Вне графика' and flag:
                flag = False
                continue
            tempDict = {'number':idReport,'in_the_chart':flag}
            for key in listick:
                try:
                    tempDict[key] = gc.Content[row][getattr(gc,key)]
                except:
                    tempDict[key] = None
            # tempDict['columnNumber'] = gc.Content[row][gc.columnNumber]
            # tempDict['columnName'] = gc.Content[row][gc.columnName]
            # tempDict['columnName'] = gc.Content[row][gc.columnName]

            # finalityDict[tempKey][row] = {
            #     'сcall_Customer':None,          #
            #     'in_the_chart':flag,            # иникатор по графику или вне графика
            #     'room':'[]',                    # Номер помещания
            #     'number_the_Customer':None,     #
            #     'number_in_b_estimate':None,    #
            #     'number_in_order':None,         #
            #     'name_id':None,                 #
            #     'dimension':None,               #
            #     'value':None,                   #
            #     'code':None,                    #
            #     'date_of_the_call':None,        # Дата предъявления объёмов по графику
            #     'actual_date':None,             # Фактическая дата приёмки
            #     'id_contractor':None,           # id подрядчика по заявке
            #     'id_actual_contractor':None,    # id исполнителя работ
            #     'id_CC_engineer':None,          # id инженера строительного контроля принимавшиего работы
            #     'result':False,                 #
            #     'axes':None,                    # Оси в которых сдаётся объём в формате JSON
            #     'floor':None,                   #
            #     'number_report':None,           # Номер в отчёте
            #     'date_report':None,             # Дата отчёта
            #     'note':None                     # Примечания к записи
            # }
            # name = gc.Content[row][gc.columnName]
            # finalityDict[tempKey][row]['number_report'] = gc.numberReport
            # finalityDict[tempKey][row]['axes'] = gc.getAxes(gc.getBuildingAxes(re.sub(r'М ?[/\\] ?Н','М_Н', str(name))))
            # finalityDict[tempKey][row]['date_report'] = gc.dateReport
            # finalityDict[tempKey][row]['room'] = getRoom(name)
            # finalityDict[tempKey][row]['floor'] = getFloor(gc, row)
            # finalityDict[tempKey][row]['note'] = gc.Content[row][gc.note]
            # finalityDict[tempKey][row]['date_of_the_call'] = None if type(gc.Content[row][gc.rowDateReport]) == str else gc.Content[row][gc.plane]
            # finalityDict[tempKey][row]['actual_date'] = None if type(gc.Content[row][gc.rowDateReport]) == str else gc.Content[row][gc.fact]
            # finalityDict[tempKey][row]['id_contractor'] = gc.getContractor(str(gc.Content[row][gc.contractor_sRepresentative]))
            # finalityDict[tempKey][row]['id_actual_contractor'] =  gc.getContractor(str(gc.Content[row][gc.executor]))
            # finalityDict[tempKey][row]['id_CC_engineer'] = gc.getEngineerCC(gc.Content[row][gc.colCCEngeneer])
            
            rowClass = Row({row:tempDict})

    # for key in finalityDict:
    #     for keyTwo in finalityDict[key]:
    #         if len(str(finalityDict[key][keyTwo]['room'])) > 2:
    #             print('+-----------------------+-----------------------+')
    #             print(key,'->',keyTwo,'room :',finalityDict[key][keyTwo]['room'])
    #             try:
    #                 print(key,'->',keyTwo,'сall_Customer:',finalityDict[key][keyTwo]['сall_Customer'])
    #                 exit(0)
    #             except:
    #                 print(key,'->',keyTwo,'сall_Customer: None')

    # Время выполнения скрипта
    print("--- %s секунд ---" %(time.time() - start_time))