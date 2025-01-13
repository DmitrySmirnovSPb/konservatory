import sys, os, json, time, re
sys.path.append(os.getcwd() + '/')
from importModul.CC_Report_class import CC_Report
from importModul.report_class import Report
from excel_class import Excel

if __name__ == '__main__':

    start_time = time.time()

    finalityDict = dict()

    theMainLink = 'C:\\Users\\d.smirnov\\Documents\\отчёт\\'
    target = theMainLink + 'automatic general report.xlsx'
    startRow = 5 # Начальная строка данных в файле. agr.maxRow - последняя строка данных в файле.

    data = {
        1:{1:1,
        2:1,
        3:'12.2023 - 5845',
        4:1,
        5:'+',
        6:1,
        7:'Монтаж МК - Ферм - Зал Рубинштейна.',
        8:'',
        9:'9-27/Д-М/Н',
        10:'',
        11:'',
        12:'т.',
        13:214.54,
        14:'001/12-К-КМ-1.4',
        15:'2023-05-16',
        16:'2023-05-16',
        17:'ООО «СВАРГО» Пильгин Г.А.',
        18:'ООО «СВАРГО» Пильгин Г.А.',
        19:'',
        20:'',
        21:'Тарасов Денис Александрович',
        22:''},
    }
    
    match = r'^Отчет №\d*.*\.xlsx$'
    listick = ['columnNumber',          # Столбец с номером по порядку в отчёте
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

    start = 23
    finish =24

    dictAuto = {
        1:'call_Customer',              
        2:'number_the_Customer',
        3:'numberInBEstimate',
        4:'number',
        5:'in_the_chart',
        6:'number_in_order',
        7:'columnName',
        8:'roomNumbers',
        9:'',
        10:'',
        11:'',
        12:'unitOfMeasurement',
        13:'countColumn',
        14:'workingDocumentationColumn',
        15:'plane',
        16:'fact',
        17:'contractor_sRepresentative',
        18:'executor',
        19:'note',
        20:'dateSED',
        21:'colCCEngeneer',
        22:''
    }
    for year in range(start, finish + 1):
        # Загружаем по новой automatic ***general report.xlsx***
        agr = Excel(target)
        agr.initSheet('отчёт')

        listReport = []
        if agr.maxRow > 5:
            for row in range(5,agr.maxRow + 1):
                if agr.row[4] not in listReport:
                    listReport.append(agr.row[4])
        path = theMainLink + '20%s\\'%year
        # path = 'C:\\Users\\d.smirnov\\Documents\\отчёт\\2023\\'
        rez = os.listdir(path)
        result = []
        # Считывание всех файлов а папке path и поиск файла с отчётом
        for string in rez:
            temp = re.search(match, string)
            if temp:
                result.append(temp[0])

        for item in result:
            scheduledCall = True            # Вызов по графику

            gc = CC_Report(link = item, globalLink = path, Sheet = 'Отчёт', nameDB = 'polytechstroy')
            print(int(str(gc.date)[:4]))
            if gc.number in listReport and year == int(str(gc.date)[:4]):
                continue # Если отчет есть в файле (automatic general report.xlsx), то переходим к следующему отчёту
            numberReport = gc.number # 4 (D) - Номер отчёта
            for row in range(gc.startRow,gc.end):
                agr.addALine(gc.Content[row])
                print(gc.Content[row])
            break
            
            agr.saveFile()

            exit(item)

    # Время выполнения скрипта
    print("--- %s секунд ---" %(time.time() - start_time))