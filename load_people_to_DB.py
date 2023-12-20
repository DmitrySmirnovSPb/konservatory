import re, os, json, time
start_time = time.time()
from importModul import get
from excel_class import Excel
from write_class import Write
from DB_class import DB

if __name__ == "__main__":
    start_time = time.time()
    # Получаем текущую дерикторию скрипта
    rootLink = os.path.dirname(os.path.realpath(__file__))
    # Загружаем ссылку на файл Excel в переменную `link`
    link = rootLink + '/data/people.xlsx'
    # Получаем объект класса Excel
    ExcelObj = Excel(link)
    # получаем список названия листов
    sheets = ExcelObj.getSheets()
    # Инициируем нужный нам лист
    ExcelObj.initSheet(sheets[0])
    # Получаем все данные с листа записанные в формате словаря
    Content = ExcelObj.getContent()

    tableName = 'people'
    db = DB()
    temp = list()
    db.clearTable(tableName)
    for row in Content:
        if row == 1:
            data = [list(Content[1].values())]
        else:
            temp.append(list(Content[row].values()))
    data.append(temp)

    result = db.insert(tableName, data)

    print(result)

print("--- %s seconds ---" %(time.time() - start_time))