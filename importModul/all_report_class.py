import sys, re, json, os, datetime
from excel_class import Excel
from DB_class import DB

class All_Report(Excel):

    fileName ='Сводный отчет СК по вызову стройконтроля.xlsx'
    folder = '\\\\srv-fs-02.stroy.local\\Shares\\Консерватория\\21. Строительный контроль\\Еженедельные отчеты\\'

    def __init__(self):
        link = self.folder + self.fileName
        super().__init__(link)
        self.db = DB()
    
    # Получить очищенные данные из файла 
    def getClearContent(self, startR = 1, endR = 0, startC = 1, endC = 0):
        content = self.getContent(startR, endR, startC, endC)
        return content

    def update_xlsx(self, src, dest):
        # Откройте xlsx-файл для чтения
        wb = load_workbook(filename = dest)
        # Получите текущий активный лист
        ws = wb.get_active_sheet()
        # Вы также можете выбрать конкретный лист
        # на основе названия листа
        # ws = wb.get_sheet_by_name("Лист1")
        # Откройте файл csv
        with open(src) as fin:
            # прочитайте csv
            reader = csv.reader(fin)
            # пронумеруйте строки, чтобы вы могли
            # получить индекс строки для xlsx
            for index,row in enumerate(reader):
                # При условии, что строка разделена пробелами
                # Разделите строку на ячейки (столбцы)
                row = row[0].split()
                # Получите доступ к конкретной ячейке и присвойте
                # значение из строки csv
                ws.cell(row=index,column=7).value = row[2]
                ws.cell(row=index,column=8).value = row[3]
        # сохраните csv-файл
        wb.save(dest)