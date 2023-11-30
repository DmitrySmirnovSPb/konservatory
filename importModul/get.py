from DB_class import DB
from excel_class import Excel
import re, json

# Получить из строки первые цифры, если цифр нет, то вращает 1.1 Если flag = True - считается только с начала строки
def getNumber(data: str, flag = True):
    match = r'\d{1,4}'
    if flag: match = '^' + match
    temp = re.findall(match, data)
    if temp == []: return 1
    return int(temp[0])
# Добавить пробел между цифрой и буквой если этого пробела нет
def addSpaceNumber(string: str):
    test = '0123456789'
    result = ''
    endString = len(string)-1
    for i in range(endString):
        if string[i] in test and string[i+1] != ' ' and string[i+1] not in test:
            result += string[i]+' '
        else: result += string[i]
    return result + string[endString]
# Перезаписать записи в таблицу DB
def addAnEntryToDB(data: list):
    nameTable = data[0]
    listTable = ['chapter','estimate_number','notes','justification','name_of_works_and_materials','contractor','dimension']
    result = False
    if nameTable in listTable:
        db = DB()
        db.clearTable(nameTable)
        result = db.insert(nameTable, getData(data))
    return result
# Получить данные из ячейки с номером и названием раздела
def getData(data: list):
    temp = list()
    match = r'Раздел \d*\. '
    if data[0] == 'dimension' or data[0] == 'chapter':
        tempAr = list(data[3])
        for text in tempAr:
            if data[0] == 'chapter':
                num = getNumber(text, False)
                text = re.sub(match, '', text, flags=re.I)
            else: num = getNumber(text)
            temp.append([text, num])
        return [data[1],temp]
    elif data[0] == 'contractor':
        return [data[1],getContractor(list(data[3]))]
    else:
        return [data[1],list(data[3])]
# Получить даннные из файла с подрядчиками    
def getContractor(contractorList: list):
    tempList = []
    ws = Write('data\\contractor.txt')
    data = ws.getDictionary(';')
    for temp in contractorList:
        if temp in data:
            tempList.append([temp,data[temp]])
    return tempList
# Получть ID по названию раздела
def getChapterID(i):
    db = DB()
    where = '`name` = "' + re.sub(r'Раздел \d*\. ', '', db.escapingQuotes(i) , flags=re.I) + '"'
    result = db.select('chapter',{'columns':['id'],'where':[where]})
    return result[0] if result != False else False

def getContentCellFormatNumber(ExcelObj: Excel, r: int, c: int):
    formatNum = ExcelObj.getCellFormatNumber(r, c)
    value = ExcelObj.getCell(r,c)
    valStr = str(value)
    if type(value) == float:
        if (formatNum == '0.00' and int(value*10) == value*10) or (formatNum == '0.000' and int(value*10) == value*10):
            valStr += '0'
        elif formatNum == '0.000' and int(value*100) == value*100:
            valStr += '00'
    elif type(value) == int: return json.dumps({1:str(value)})
    lst = valStr.split('.')
    result = dict()
    i = 1
    for num in lst:
        result[i] = str(num)
        i += 1
    return json.dumps(result)
# Записать данные в итоговую строку
def setDataRow(i,num):
    keys = [
        'chapter_id',
        'number_in_order',
        'estimate_id',
        'estimate_number',
        'justification_id',
        'Year',
        'first_notes_id',
        'second_notes_id',
        'mini_header',
        'grey',
        'name_id',
        'contractor_id',
        'uom',
        'value',
        'cost',
        'tbas',
        'wpi',
        'executive_documentation']
    for key in keys:
        match key:
            case 'chapter_id':# y
                result = chapter_id
            case 'number_in_order':
                result = i[1]
            case 'estimate_id':
                result = getEstimateID(i[2])
            case 'estimate_number':
                result = getEstimateNumber(i)
            case 'justification_id':
                result = getJustificationID(i)
            case 'Year':# y
                result = year
            case 'first_notes_id':# y
                result = firstNote
            case 'second_notes_id':# y
                result = secondNote
            case 'grey':
                i.getFontColorCell(r, c)
                result = getGrey(i)
            case 'name_id':
                result = getNameID(i)
            case 'contractor_id':
                result = getContractorID(i)
            case 'uom':
                result = getUOM(i)
            case 'value':
                result = getValue(i)
            case 'cost':
                result = getCost(i)
            case 'tbas':
                result = getTBAS(i)
            case 'wpi':
                result = get(i)
            case 'executive_documentation':
                result = getExecutiveDocumentation(i)
        resultSet[num][key] = result