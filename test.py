import sys, os, json, time, re
sys.path.append(os.getcwd() + '/')
from importModul.CC_Report_class import CC_Report
from importModul.row_class import Row
from importModul.report_class import Report

if __name__ == '__main__':

    start_time = time.time()

    finalityDict = dict()

    match = r'^Отчет №\d*.*\.xlsx$'

    path = '//srv-fs-02.stroy.local/Shares/Консерватория/21. Строительный контроль/Еженедельные отчеты/2024/'

    rez = os.listdir(path)
    result = []
    # Считывание всех файлов а папке path и поиск файла с отчётом
    for string in rez:
        temp = re.search(match, string)
        if temp:
            result.append(temp[0])
    result.sort()
    # for t in result: print(t)
    # exit(0)
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
    result = ['Отчет №014 СК по вызову стройконтроля 2024-04-04-04-010.xlsx']
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
            if gc.Content[row][gc.columnNumber] == 'Вне графика' and flag:
                flag = False
                continue
            # print(f'\n+-- {item} --+\n')
            name = gc.Content[row][gc.columnName]
            tempDict = {'number':idReport,'in_the_chart':flag}
            for key in listick:
                try:
                    tempDict[key] = gc.Content[row][getattr(gc,key)]
                except:
                    tempDict[key] = None
            tempDict['number_in_order'] = gc.Content[row][getattr(gc,'columnNumber')]
            tempDict['number_in_b_estimate'] = gc.Content[row][getattr(gc,'numberInBEstimate')]

            rowClass = Row({row:tempDict})
        #     if row > 34:
        #         print("--- %s секунд ---" %(time.time() - start_time))
        #         exit(0)
        # exit(0)

    # Время выполнения скрипта
    print("--- %s секунд ---" %(time.time() - start_time))