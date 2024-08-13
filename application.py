import sys, os, json, time, re
sys.path.append(os.getcwd() + '/importModul/')
from excel_class import Excel
from all_report_class import All_Report

if __name__ == '__main__':

    start_time = time.time()

    exAll = All_Report()

    exAll.initSheet('отчёт')
    exAll.getClearContent(endC=17, startR = 5)

    gap = '@$#~'

    replacement = {
        '\n':' ','. ':'.', 'ао«дока':'ао «дока', 'cк дока':'ск'+gap+'дока', '«':'', '»':'','ск ':'','-центр':'','-инжиниринг':'', 'художественно-реставрационная группа ':'','нв билдинг':'нв'+gap+'билдинг','ук арт-глас':'арт-глас','"':'','новое время':'новое'+gap+'время','политех строй':'политехстрой', 'лепной двор':'лепной'+gap+'двор','ван строй':'ван'+gap+'строй','метеор лифт':'метеор'+gap+'лифт', 'политехстрой-сварго':'политехстрой', 'пгс систем':'пгс'+gap+'систем', 'янтарная прядь-паркет':'янтарная'+gap+'прядь-паркет', 'гранит тех':'гранит'+gap+'тех', 'буга антон владиславович':'буга', 'реставрация. проектирование. строительство':'р.п.с.', 'центральный реставрационный комплекс':'црк'
    }
    List = []
    ListName = []
    for row in exAll.clearContent:
        if exAll.clearContent[row][14] != None:
            string = exAll.clearContent[row][14]

            for old, new in replacement.items():
                string = string.lower().replace(old,new)

            temp = string.split()
            try:
                tempStr = temp[1].lower().replace(gap,' ')
                if tempStr not in List:
                    List.append(tempStr)
            except Exception as e:
                print(e,' -> ',temp)
            try:
                tempStr = temp[2]
                if tempStr not in ListName:
                    ListName.append(tempStr)
            except Exception as e:
                print(e,' -> ',temp)

    List.sort()
    for t in List:
        id = exAll.db.select('contractor',{'columns': ['id'], 'where' : ['`name` = "'+ str(t) +'"']})
        print(t, 'id =', id)
    print('\n-----------------------------------------------------\n')
    ListName.sort()
    for t in ListName:
        id = exAll.db.selectAll('people',{'columns': ['initials','l_name','company_id'], 'where' : ['`l_name` = "'+ str(t) +'"']})
        company = exAll.db.select('contractor', {'columns': ['abbreviated_name'], 'where' : ['`id` = "'+ str(id[0]['company_id']) +'"']})
        print(company, id[0]['l_name'],id[0]['initials'])
    # Время выполнения скрипта
    print("--- %s секунд ---" %(time.time() - start_time))