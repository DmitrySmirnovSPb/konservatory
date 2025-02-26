import sys, os, json, time, re
sys.path.append(os.getcwd() + '\\importModul\\')
from call_class import Call_Customer

if __name__ == '__main__':

    start_time = time.time()

    finalityDict = dict()

    match = r'^\d\d ЗАЯВКА на вызов заказчика.*\.xlsx$'

    start = 23
    finish =25
    theMainLink = '\\\\srv-fs-02.stroy.local\\Shares\\Консерватория\\21. Строительный контроль\\Графики вызова Заказчика\\'

    for year in range(start, finish + 1):

        path = theMainLink + '_20%s вызов заказчика\\'%year
        rez = os.listdir(path)
        result = []
        # Считывание всех файлов а папке path и поиск файла с отчётом
        for string in rez:
            temp = re.search(match, string)
            if temp:
                result.append(temp[0])
        result.sort()
        # for link in result:
        #     print(link)

        # result = ['Отчет №025 СК по вызову стройконтроля 2024-06-20-06-26.xlsx']
        for item in result:

            cc = Call_Customer(link = item, globalLink = path, Sheet = 'Лист1', nameDB = 'polytechstroy')
            exit(0)
            for key in range(cc.startRow, cc.end + 1):
                pass
                # try:
                    
                # except:
                    

    # Запись в БД report, проверка существования записи по дате отчёта
            idReport = report.checkingTheRecord()
            check = False

            if idReport != False:
                temp =gc.db.selectAll('сс_accepted_volumes',{'columns':['id'], 'where':['`number` = ' + str(idReport)]})
                print("set DB", temp[0])

                if temp[0] != None:
                    check = True

            flag = True
            for row in range(gc.startRow, gc.end + 1):
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
                tempDict['number_in_b_estimate'] = gc.Content[row][getattr(gc,'numberInBEstimate')]
                rowClass = Row({row:tempDict}, gc.db,check = check)

        # Время выполнения скрипта
        print("--- %s секунд ---" %(time.time() - start_time))