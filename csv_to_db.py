import os #for file removal
import sqlite3
import csv
import pandas as pd

if os.path.exists('sipuni.db'):
    os.remove('sipuni.db')
else:
    print('file does not exist')

con = sqlite3.connect('sipuni.db')
print('DB created')
c = con.cursor()
print('cursor placed')
c.execute(
    """
    CREATE TABLE calls (
        Type TEXT,
        Status TEXT,
        Time TEXT,
        Scheme TEXT,
        Origin TEXT,
        Destination TEXT,
        Operator TEXT,
        CallDuration INTEGER,
        ConversationDuration INTEGER,
        AnswerTime INTEGER,
        NewClient INTEGER,
        CallbackStatus TEXT,
        CallbackTime INTEGER
    );
    """
)
print('table created')

#file name
fname = "stat.csv"

data = pd.read_csv(fname, delimiter = ';')
df = pd.DataFrame(data, columns = ['Тип', 'Статус', 'Время', 'Схема', 'Откуда', 'Куда', 'Кто ответил', 'Длительность звонка', 'Длительность разговора', 'Время ответа', 'Новый клиент', 'Состояне перезвона', 'Время перезвона'])
df_db = [(i['Тип'], i['Статус'], i['Время'], i['Схема'], i['Откуда'], i['Куда'], i['Кто ответил'], i['Длительность звонка'], i['Длительность разговора'], i['Время ответа'], i['Новый клиент'], i['Состояне перезвона'], i['Время перезвона']) for index, i in df.iterrows()]

c.executemany("INSERT INTO calls (Type, Status, Time, Scheme , Origin, Destination, Operator, CallDuration, ConversationDuration, AnswerTime, NewClient, CallbackStatus, CallbackTime) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);", df_db)
con.commit()
#print('commit')
con.close()
print('closed')