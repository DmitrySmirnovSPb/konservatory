import sys, os, json, time, re
sys.path.append(os.getcwd() + '\\importModul\\')
from excel_class import Excel

if __name__ == '__main__':

    start_time = time.time()

    linkAll = '\\\\srv-fs-02.stroy.local\\Shares\\Консерватория\\21. Строительный контроль\\Еженедельные отчеты\\Сводный отчет СК по вызову стройконтроля.xlsx'

    exAll = Excel(linkAll)
    exAll.initSheet('отчёт')
    contentAll = exAll.getContent(endC=17)
    print(contentAll[16276])

    # Время выполнения скрипта
    print("--- %s секунд ---" %(time.time() - start_time))