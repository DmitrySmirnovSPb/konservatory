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
#####################################################################################################################
#                                                                                                                   #
# Структура результирующих данных                                                                                   #
#   Cell:[str:Table name,list: List Column,list: List of exceptions, set: Data]                                     #
#           Cell                номер столбца в файле Экселя сметы                                                  #
#           Table name          Название таблице в базе данных MySQL                                                #
#           List Column         Список ячеек которые заносятся в таблице Table name                                 #
#           List of exceptions  Список исключений данных в ячейке столбца Cell кроме значение None                  #
#           Data                Полученные данные в виде множества                                                  #
#                                                                                                                   #
#####################################################################################################################
TotalResult = {1:['chapter',['name','number'],[],set()],
               2:['estimate_number',['estimate'],['Номер сметы'], set()],
               3:['notes',['note'],['Позиция сметного расчета / Номер'],set()],
               4:['justification',['position'],['Позиция сметного расчета / Обоснование', 'Счет', 'СЧЕТ'],set()],
               5:['name_of_works_and_materials',['name'],['Наименование конструктивных решений (элементов), комплексов (видов) работ', 'Итого сумма позиций', 'Итого сумма позиций', 'Временные здания и сооружения – 1,44%', 'Зимнее удорожание - 1,41%', 'Итого', 'Расчетная стоимость единицы', 'Всего на физобъем', 'в том числе материалы', 'Стоимость единицы', 'Всего с НДС', 'Дополнительные работы:', 'Всего, включая дополнительные работы', 'Итого по смете', 'Итого по разделу'],set()],
               6:['contractor',['name','full_name'],['3','Подрядчик'],{'ПОЛИТЕХСТРОЙ'}],
               7:['dimension',['name','multiplicity'],['Единица измерения'],set()]}

for i in Content:
    for j in range(1,ExcelObj.maxColumn + 1):
        if j in TotalResult:
            listExceptions = [None,'None'] + TotalResult[j][2]
            cell_str = " ".join(str(Content[i][j]).split())
            if j == 1:
                if cell_str.find('Раздел') >= 0: result = cell_str # re.sub(match_1, '', cell_str, flags=re.I)
                else: continue
            elif j == 2 : result = cell_str.split('Поз.')[0].replace('ЛС ','')
            elif j == 3 or j == 7 :
                if isinstance(Content[i][j], int) or isinstance(Content[i][j], float): continue
                else:
                    if j == 7: cell_str = cell_str.lower()
                    result = get.addSpaceNumber(cell_str)
            else: result = cell_str
            if result in listExceptions: continue

            TotalResult[j][3].add(result.strip())

# for i in TotalResult:
#     if i == 7: 
#         for j in getData(TotalResult[i]):
#             print(j)
#     addAnEntryToDB(TotalResult[i])

#############################################################################
#           Занесение основных данных сметы в DB                            #
#############################################################################
#       Формириование строк таблицы basic_estimate не более 10000 строк     #
#############################################################################
basicEstimite = list()
year = 2014
firstNote = ''
secondNote = ''
chapter_id = 0
db = DB()
resultSet = set()

for i in Content:
    contractor_id = None
    flag = True
    typeCell = type(Content[i][1])
    if(typeCell == type(None) and type(Content[i][2]) == type(None)):
        if type(Content[i][3]) == str:
            if ' года' in Content[i][3]:
                year = get.getNumber(Content[i][3])
                flag = False
                continue
            else:
                if type(Content[i+1][2]) == type(None) and type(Content[i+1][3]) == str:
                    where = '`note` = "' + str(Content[i][3]) + '"'
                    temp = db.select('notes',{'columns':['id'],'where':[where]})
                    firstNote = '' if temp == None or temp == False or len(temp) <= 0 else str(temp[0])
                    where = '`note` = "' + str(Content[i+1][3]) + '"'
                    temp = db.select('notes',{'columns':['id'],'where':[where]})
                    secondNote = '' if temp == None or temp == False or len(temp) <= 0 else str(temp[0])
                    flag = False
                elif firstNote == '':
                    where = '`note` = "' + db.escapingQuotes(str(Content[i][3])) + '"'
                    temp = db.select('notes',{'columns':['id'],'where':[where]})
                    secondNote = '' if temp == None or temp == False or len(temp) <= 0 else str(temp[0])
                    flag = False
        elif type(Content[i][3]) == type(None) and type(Content[i][5]) == str:
            flag = False
            if 'Итого сумма позиций' == Content[i][5]:
                print(i,'Итого сумма позиций')
            elif 'Временные здания и сооружения' in Content[i][5]:
                print(i, '1.44% - Старт:')
            elif 'Зимнее удорожание' in Content[i][5]:
                print(i, '1.41% - Старт')
            else: print(i,'******* Столбец 5 (E) *******')
            
#            print(i,'год',year,'=>',firstNote,secondNote)
    # elif(typeCell == float): print('Тип FLOAT')
    elif typeCell == int:
        startTbas = i
        startWpi = i
        if Content[i][5] != None:
            step = get.getContentCellFormatNumber(ExcelObj, i, 1)
            where = '`name` = "' + str(Content[i][6]) + '"'
            temp = db.select('contractor',{'columns':['id'],'where':[where]})
            contractor_id = 'null' if temp == None or temp == False or len(temp) <= 0 else temp[0]
            print(i,f'**** {year} chapter_id {chapter_id} INIT({step}) contractor_id {contractor_id}, firstNote {firstNote}, secondNote {secondNote} ****')
        flag = False
        firstNote = ''
        secondNote = ''
    elif typeCell == float:
        if Content[i][5] != None:
            step = get.getContentCellFormatNumber(ExcelObj, i, 1)
            where = '`name` = "' + str(Content[i][6]) + '"'
            temp = db.select('contractor',{'columns':['id'],'where':[where]})
            contractor_id = 'null' if temp == None or temp == False or len(temp) <= 0 else temp[0]
        print(i,f'**** {year} chapter_id {chapter_id} FLOAT({step}) contractor_id {contractor_id}, firstNote {firstNote}, secondNote {secondNote} ****')

        flag = False
    elif(typeCell == str):
        if 'Раздел' in str(Content[i][1]):
            chapter_id = get.getChapterID(Content[i][1])
            flag = False
            year = 2014
            firstNote = ''
            secondNote = ''
            startTbas = i
            startWpi = i
    else:
        print(i,'год', year, '=>', str(firstNote) + ', ' + str(secondNote))
        flag = False
    if flag: print (i,'!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
    if i >= 2023 : break