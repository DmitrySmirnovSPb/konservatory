from write_class import Write
# from DB_class import DB
import os

cur_dir = os.path.dirname(os.path.realpath(__file__))

#link = input('Введите ссылку на файл: ')
linkAr = [
    'capter',
    'estimate_number',
    'justification',
    'name_of_works_and_materials',
    'notes'
]

f = Write(cur_dir + '\\data\\notes.txt')
# print(f.sort(f.getDictionary('.','int')))
# print(f.getSet(' '))

l=f.listContent
for i in l:
    print(i)
# db = DB()
# db.insert('notes',[['note'], l])

# for li in linkAr:
#     link = 'C:\\project\\.venv\\data\\'+li+'.txt'
#     f = Write(link)
#     if li == 'capter':
#         d = f.sort(f.getDictionary('.'))
#         for i in d:
#             print(i,'--',d[i])
#     else:
#         for i in f.listContent:
#             print(i)