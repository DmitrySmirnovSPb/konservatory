from DB_class import DB
from importModul import get
from excel_class import Excel
from write_class import Write
import re, os

# Получаем текущую дерикторию скрипта
rootLink = os.path.dirname(os.path.realpath(__file__))
# Загружаем ссылку на файл Excel в переменную `link`
link = rootLink + '\\data\\предвар.xlsx'
# Получаем объект класса Excel
ExcelObj = Excel(link)
# получаем список названия листов
sheets = ExcelObj.getSheets()
# Инициируем нужный нам лист
ExcelObj.initSheet(sheets[0])
# Получаем все данные с листа записанные в формате словаря
Content = ExcelObj.getContent()
# Опредиление максимального количество строк
end = ExcelObj.maxRow
map = dict()
map['chapter_id'] = dict()
map['year'] = dict()
map['notes'] = dict()
year = 2014
firstNote = ''
secondNote = ''
chapter_id = 0
db = DB()
stopChapter = 0
startChapter = 0

for i in Content:
    if 'Раздел' in str(Content[i][1]):
        year = 2014
        map['chapter_id'][i] = get.getChapterID(Content[i][1])
    elif type(Content[i][1]) == int:
        summ = 0
        total = Content[i][11]
    elif type(Content[i][3]) == str:
        if ' года' in Content[i][3]:
            year = get.getNumber(Content[i][3])
        else:
            if type(Content[i+1][2]) == type(None) and type(Content[i+1][3]) == str:
                where = '`note` = "' + str(Content[i][3]) + '"'
                temp = db.select('notes',{'columns':['id'],'where':[where]})
                firstNote = '' if temp == None or temp == False or len(temp) <= 0 else str(temp[0])
                where = '`note` = "' + str(Content[i+1][3]) + '"'
                temp = db.select('notes',{'columns':['id'],'where':[where]})
                secondNote = '' if temp == None or temp == False or len(temp) <= 0 else str(temp[0])
            elif firstNote == '':
                where = '`note` = "' + db.escapingQuotes(str(Content[i][3])) + '"'
                temp = db.select('notes',{'columns':['id'],'where':[where]})
                secondNote = '' if temp == None or temp == False or len(temp) <= 0 else str(temp[0])
    map['year'][i] = year
for p in map['chapter_id']:
    print(p,'->',map['chapter_id'][p])
