import sys, re, json, os
sys.path.append('C:/project/konservatory/data/')
sys.path.append('C:/project/konservatory/importModul/')

from DB_class import DB
import write_class
from excel_class import Excel
from importModul.get import getContent
from datetime import datetime as dt

class CC_Report(getContent):

    rowNumReport, colNumReport = 0, 0
    rowDateReport, colDateReport = 0, 0
    columName = 0
    number_СС_Report = 0

    def __init__(self, link, nameDB, globalLink, Sheet):
        getContent.__init__(self, link, nameDB, globalLink, Sheet)
        self.getNumberAndDate()

    def getNumberAndDate(self):
        r = r"^ОТЧЁТ №\d+ "
        rDate = r'за период с'
        rName = r'к освидетельствованию'
        rNumber = r'^№ п/п$'
        for row in self.Content:
            for column in self.Content[row]:
                if self.Content[row][column] == None: temp = ''
                else: temp = str(self.Content[row][column])
                if re.search(r,temp): self.rowNumReport, self.colNumReport = row, column
                if re.search(rDate,temp): self.rowDateReport, self.colDateReport = row, column
                if re.search(rName,temp): self.columName = column
                if re.search(rNumber,temp): self.number_СС_Report = column
            if self.rowNumReport != 0 and self.rowDateReport != 0 and self.columName != 0 and self.number_СС_Report != 0: break
        self.numberReport = int(re.findall(r'\d+',re.findall(r'№\d+\b', self.Content[self.rowNumReport][self.colNumReport])[0])[0])
        self.dateReport = dt.strptime(re.findall(r'\d+\.\d+\.\d+', self.Content[self.rowNumReport][self.colNumReport])[0], r'%d.%m.%Y')
        listDate = re.findall(r'\d+\.\d+\.\d+', self.Content[self.rowDateReport][self.colDateReport])
        self.startReport  = dt.strptime(listDate[0], r'%d.%m.%Y')
        self.finishReport = dt.strptime(listDate[1], r'%d.%m.%Y')