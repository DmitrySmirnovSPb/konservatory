from openpyxl import load_workbook, Workbook
from openpyxl.styles import Font, Color, numbers


class Excel(object):

    def __init__(self, link: str):
        try:
            self.wb = load_workbook(link)
            self.error = None
        except:
            self.error = "Файл по адресу " + link + " не удалось открыть"
            print()
            print(self.error)
            print()
# Инициация листа по названию sheetName
    def initSheet(self, sheetName: str):
        self.Sheet = self.getSheeltByName(sheetName)
        self.maxRow = self.Sheet.max_row
        self.maxColumn = self.Sheet.max_column
# Получить список листов в книге
    def getSheets(self):
        return self.wb.sheetnames
# Получить лист по названию
    def getSheeltByName(self, name: str):
        return self.wb[name]
# Получить контент с активного листа со строки startR по строку endR, колонки от startC по колонку endC
    def getContent(self, startR = 1, endR = 0, startC = 1, endC = 0):
        rows = self.maxRow if endR == 0 or self.maxRow < endR else endR
        columns = self.maxColumn if endC == 0 or self.maxColumn < endC else endC
        result = {}
        for i in range(startR, rows + 1):
            result[i] = self.getLineContent(i, startC, columns)
        return result
# Возвращает с листа Sheet строку с номером line со столбца с № start по № colums в формате словаря с ключами по № столбца
    def getLineContent(self, line, start, columns):
        lineDict = {}
        for i in range(start, columns + 1):
            lineDict[i] = self.getCell(line, i)
        return lineDict
# Возвращает с листа Sheet колонку с номером line со строки с № start по № end в формате словаря с ключами по № столбца
    def getColumContent(self, column: int, start, end):
        columnDict = {}
        for i in range(start, end + 1):
            columnDict[i] = self.getCell(i, column)
        return columnDict
# возвращает значение ячейки № строки (r), № столбца (c) листа Sheet
    def getCell(self, r: int, c: int):
        return self.Sheet.cell(row=r, column=c).value
# возвращает значение ячейки в фомате А1 листа Sheet
    def getCellLitter(self, coordinates: str):
        return self.Sheet[coordinates].value
# Возвращает цвет шрифта в ячейке в формате FF000000
    def getFontColorCell(self, r: int, c: int):
        return self.Sheet.cell(row=r, column=c).font.color.rgb
# Возврщает числовой формат ячейки с координатами r и c
    def getCellFormatNumber(self, r: int, c: int):
        return self.Sheet.cell(row=r, column=c).number_format