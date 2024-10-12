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

    for row in ccav.Content:
        if row < 16276: continue #5
        # if row > 35: break

        data = {}
        # В графике вызова Заказчика или нет
        data['in_the_chart'] = True if ccav.Content[row][5] == '+' else False
        # Номер заявки вызова заказчика
        data['call_Customer'] = ccav.Content[row][1]
        # номер в заявке вызова Заказчика
        data['number_the_Customer'] = ccav.Content[row][2]
        # Предпологаемый номер по порядку в смете контракта в формате JSON или Null
        data['number_in_b_estimate'] = ccav.Content[row][3]
        # id отчёта report -> id
        data['number'] = ccav.Content[row][4]
        # номер по порядку в отчёте
        data['number_in_order'] = ccav.Content[row][6]
        # id Названия работы или материала. name_of_works_and_materials -> id
        data['name_id'] = ccav.Content[row][7]
        # id Единицы измерения dimension -> id
        data['dimension'] = ccav.Content[row][8]
        # Количество фактически принятых работ
        data['value'] = ccav.Content[row][9]
        # Шифр проекта, ЖАН или другое обоснование работ в формате JSON или Null
        data['code'] = ccav.Content[row][10]
        # Дата вызова заказчика (План)
        data['date_of_the_call'] = ccav.Content[row][11]
        # Дата фактического предъявления работ
        data['actual_date'] = ccav.Content[row][12]
        # ID представителя субподрядчика people -> id
        data['id_contractor'] = ccav.Content[row][13]
        # ID компании представителя субподрядчика contractor -> id
        data['id_contractor_company'] = ccav.Content[row][13]
        # ID представителя фактического исполнителя people -> id
        data['id_actual_contractor'] = ccav.Content[row][14]
        # ID компании фактического исполнителя на момент производства работ contractor -> id
        data['id_actual_contractor_company'] = ccav.Content[row][14]
        # ID инженера строительного контроля предоставившего информацию people -> id
        data['id_CC_engineer'] = ccav.Content[row][17]
        # Результат предъявления работ:
        #   1 - Принято
        #   2 - Не принято
        #   3 - Не предъявлено
        #   4 - Принято в предыдущий период
        data['result'] = ccav.Content[row][15]
        # Оси в которых производились работы в формате JSON или Null
        data['axes'] = ccav.Content[row][7]
        # Номера помещений в формате JSON или Null
        data['room'] = ccav.Content[row][7]
        # Этаж или отметки в формате JSON или Null
        data['floor'] = ccav.Content[row][7]
        # Примечание
        data['note'] = ccav.Content[row][15]

        print(row)

        srtdb = SRTDB(tableName, db)

        srtdb.dataInitiation(data)

        # print()

        # exit(0)

    # Время выполнения скрипта
    print("--- %s секунд ---" %(time.time() - start_time))