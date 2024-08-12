import sys, os, json, time, re
sys.path.append(os.getcwd() + '/importModul/')
from excel_class import Excel
from all_report_class import All_Report

if __name__ == '__main__':

    start_time = time.time()

    exAll = All_Report()
    exAll.initSheet('отчёт')
    contentAll = exAll.getClearContent(endC=17, startR = 5)
    gap = '@$#~'
    # name = 'Янтарная Прядь'
    replacement = {
        '\n':' ','. ':'.', 'ао«дока':'ао «дока', 'cк дока':'ск'+gap+'дока', '«':'', '»':'','ск ':'','-центр':'','-инжиниринг':'', 'художественно-реставрационная группа ':'','нв билдинг':'нв'+gap+'билдинг','ук арт-глас':'арт-глас','"':'','новое время':'новое'+gap+'время','политех строй':'политехстрой', 'лепной двор':'лепной'+gap+'двор','ван строй':'ванстрой','метеор лифт':'метеор'+gap+'лифт', 'политехстрой-сварго':'политехстрой', 'пгс систем':'пгс'+gap+'систем', 'янтарная прядь-паркет':'янтарная'+gap+'прядь-паркет', 'гранит тех':'гранит'+gap+'тех', 'буга антон владиславович':'буга', 'реставрация. проектирование. строительство':'р.п.с.', 'центральный реставрационный комплекс':'црк'
    }
    List = []
    for row in contentAll:
        if contentAll[row][14] != None:
            # print(contentAll[row][14])
            string = contentAll[row][14].lower()
            for old, new in replacement.items():
                # print(old,'->', new)
                string = string.replace(old,new)
            # print(string)
            temp = string.split()
            # print(temp)
            # exit()
            try:
                tempStr = temp[1].lower().replace(gap,' ')
                if tempStr not in List:
                    List.append(tempStr)
            except Exception as e:
                print(e,' -> ',temp)
        # if contentAll[row][14] != None and name in contentAll[row][14]:
        #    print(f'{contentAll[row][14]}: отчёт №{contentAll[row][4]}: {contentAll[row][7]} ---> {contentAll[row][9]} {contentAll[row][8]}\n')
    List.sort()
    for t in List:
        print(t)
    # Время выполнения скрипта
    print("--- %s секунд ---" %(time.time() - start_time))