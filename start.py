from getpass import getpass
from mysql.connector import connect, Error, errorcode
import write_class as ws

def connectToDB(mydb):
    print('OK\n' + str(mydb))

config = {
    'host':     '127.0.0.1',
    'user':     'root',
    'password': '12@preli@1961',
    'database': 'polytechstroy',
    'port':     '3307'
}

if __name__ == '__main__':
    try:
        mydb = connect(**config)
        connectToDB(mydb)
    except Error as e:
        if e.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
        elif e.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(e)
    else:
        mydb.close()