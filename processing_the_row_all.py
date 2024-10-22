import sys, os, json, time, re
sys.path.append(os.getcwd() + '/')
from importModul.get import getContent
from DB_class import DB
from set_row_to_db_class import SRTDB

if __name__ == '__main__':

    start_time = time.time()

    globalLink = '\\\\srv-fs-02.stroy.local\\Shares\\Консерватория\\21. Строительный контроль\\Еженедельные отчеты\\'
    link = 'Сводный отчет СК по вызову стройконтроля.xlsx'
    tableName = 'сс_accepted_volumes'
    Sheet = 'отчёт'
    
    ccav = getContent(link = link, globalLink = globalLink, Sheet = Sheet)
    db = DB()
    # Очистка таблицы сс_accepted_volumes
    # db.clearTable('сс_accepted_volumes')
    #######################################       Список полей dictField      ###########################################
    # in_the_chart                  В графике вызова Заказчика или нет                                                  #
    # call_Customer                 Номер заявки вызова заказчика                                                       #
    # number_the_Customer           номер в заявке вызова Заказчика                                                     #
    # number_in_b_estimate          Предпологаемый номер по порядку в смете контракта в формате JSON или Null           #
    # number                        ID отчёта report -> id                                                              #
    # number_in_order               номер по порядку в отчёте                                                           #
    # name_id                       ID Названия работы или материала. name_of_works_and_materials -> id                 #
    # dimension                     ID Единицы измерения dimension -> id                                                #
    # value                         Количество фактически принятых работ                                                #
    # code                          Шифр проекта, ЖАН или другое обоснование работ в формате JSON или Null              #
    # date_of_the_call              Дата вызова заказчика (План)                                                        #
    # actual_date                   Дата фактического предъявления работ                                                #
    # id_contractor                 ID представителя субподрядчика people -> id                                         #
    # id_contractor_company         ID компании представителя субподрядчика contractor -> id                            #
    # id_actual_contractor          ID представителя фактического исполнителя people -> id                              #
    # id_actual_contractor_company  ID компании фактического исполнителя на момент производства работ contractor -> id  #
    # id_CC_engineer                ID инженера строительного контроля предоставившего информацию people -> id          #
    # result                        Результат предъявления работ:                                                       #
    #                                 1 - Принято                                                                       #
    #                                 2 - Не принято                                                                    #
    #                                 3 - Не предъявлено                                                                #
    #                                 4 - Принято в предыдущий период                                                   #
    # axes                          Оси в которых производились работы в формате JSON или Null                          #
    # room                          Номера помещений в формате JSON или Null                                            #
    # floor                         Этаж или отметки в формате JSON или Null                                            #
    # note                          Примечание                                                                          #
    #####################################################################################################################

    dictField = {
        'in_the_chart':5,'call_Customer':1,'number_the_Customer':2,'number_in_b_estimate':3,'number':4, 'number_in_order':6,'name_id':7,'dimension':8,'value':9,'code':10,'date_of_the_call':11,'actual_date':12,'id_contractor':13,'id_contractor_company':13,'id_actual_contractor':14,'id_actual_contractor_company':14,'id_CC_engineer':17,'result':15,'axes':7,'room':7,'floor':7,'note':15
    }

    for row in ccav.Content:
        if row < 5: continue #5  16276
        # if row > 35: break
#  Объявление словаря для строки, занесение значений из строки файла по адресу link
        data = {}
        for key, column in dictField.items():
            if key == 'in_the_chart':
                data[key] = True if ccav.Content[row][column] == '+' else False
            else:
                data[key] = ccav.Content[row][column]

        print(row)

        srtdb = SRTDB(tableName, db)

        srtdb.dataInitiation(data)

        # exit(0)

    # Время выполнения скрипта
    print("--- %s секунд ---" %(time.time() - start_time))