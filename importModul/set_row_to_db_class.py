from DB_class import DB

class SRTDB(object):

    data = {}

    def __init__(self, nameTable: str):
        self.nameTable = nameTable
        self.listfields = self.getFields()
        self.checkAndWriteToTheDB()
        # for field in self.listfields:
        #     print(field)

    def setFields(self, dictFields):
        error = []
        for field in dictFields:
            if field in self.listfields:
                self.data[field] = dictFields[field]
            else:
                error.append(field)
        return error

    def dataInitiation(self, dictFields):
        self.setFields(dictFields)

        if 'result' in self.data:
            self.data['result']
            lst = { 2 : 'Не принято', 3 : 'Не предъявлено', 4 : 'Принято в предыдущий период'}
            result = 1
            if self.data['result'] != None:
                for key, value in lst.items():
                    if value in self.data['result']:
                        result = key
                        break
            self.data['result'] = result
            print(self.data['result'])

    def checkAndWriteToTheDB(self):
        pass

    # Получить список полей
    def getFields(self):
        db = DB()
        lst = []
        for name in db.getListColumns(self.nameTable):
            lst.append(name[0])
        return lst