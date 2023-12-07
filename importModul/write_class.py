class Write(object):

    def __init__(self, link:str, typt_file=0, cod='utf-8'):
        self.link = link
        self.type_file = typt_file
        self.cod = cod
        self.writeFile()
        self.getContent()

# Чтение из файла
    def writeFile(self):
        try:
            self.fileWrite = open(self.link, '+rt', encoding=self.cod)
        except:
            print('Файл по адресу', self.link,'не удалось открыть')

# Чтение данных из файла записывает в self.listContent список разбитый по стокам
    def getContent(self):
        listContent = []
        for line in self.fileWrite.readlines():
            tp = line.replace('\n', '')
            temp = ' '.join(tp.split())
            listContent.append(temp)
        self.listContent = list(set(listContent))

# Разбивка строк в списке на словарь по заданой строке
    def getDictionary(self, st:str, type = 'str'):
        newAr = {}
        for line in self.listContent:
            temp = line.strip().split(st, 1)
            index = temp[0]
            if type == 'int':index = int(index)
            newAr[index] = temp[1]
        return newAr

    def getSet(self, st:str):
        newSet = set()
        for line in self.listContent:
            temp = line.strip().split(st, 1)

            newSet.add(temp[0])
        if '' in newSet:
            newSet.remove('')
        return list(newSet)

# Сортировка списка по ключам
    def sort(self, ar):
        result = dict(sorted(ar.items()))
        return result

# Освобожден6ие ресурсов    
    def __del__(self):
        self.fileWrite.close