import sqlite3
import datetime

def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
        print(e)

    return conn

#number of all calls
def number_of_calls(conn):
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM calls")

    return cur.fetchall()

#number of calls by type
def all_calls(conn):
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT Type FROM calls")

    rows = cur.fetchall()
    number_by_types_of_calls = {}
    for row in rows:
        for i in row:
            #print(i)
            cur.execute(f"SELECT COUNT(*) FROM calls WHERE Type='{i}'")
            number_by_types_of_calls[i] = cur.fetchall()[0][0]
            #print(number_by_types_of_calls)

    return number_by_types_of_calls

#number of answered incoming calls by operator
def answered_calls_by_operator(conn):
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT Operator FROM calls WHERE Type='Входящий' AND Status='Отвечен'")
    
    rows = cur.fetchall()
    number_of_calls_in_distinct_operator = {}
    for row in rows:
        for i in row:
            #print(f"SELECT COUNT(*) FROM calls WHERE Type='Входящий' AND Operator='{i}'")
            cur.execute(f"SELECT COUNT(*) FROM calls WHERE Type='Входящий' AND Status='Отвечен' AND Operator='{i}'")
            
            number_of_calls_in_distinct_operator[i] = cur.fetchall()[0][0]
    
    #print(number_of_calls_in_distinct_operator)
    return number_of_calls_in_distinct_operator

#off hours incoming calls
def off_hours_calls(conn):
    cur = conn.cursor()
    cur.execute("SELECT Time FROM calls WHERE Type='Входящий'")

    rows = cur.fetchall()
    list_of_times = []
    for row in rows:
        list_of_times.append(row[0])
        #print(row)

    return list_of_times

def call_destinations(conn):
    cur = conn.cursor()

    schemes = []
    cur.execute("SELECT DISTINCT Scheme FROM calls WHERE Type='Входящий'")
    schemes_list = cur.fetchall()
    for i in schemes_list:
        schemes.append(i[0])

    operators = []
    cur.execute("SELECT DISTINCT Operator FROM calls WHERE Type='Входящий'")
    operators_list = cur.fetchall()
    for i in operators_list:
        operators.append(i[0])

    for i in schemes:
        cur.execute(f"SELECT COUNT(*) FROM calls WHERE Type='Входящий' AND Scheme='{i}'")
        number_of_calls = cur.fetchall()
        cur.execute(f"SELECT COUNT(*) FROM calls WHERE Type='Входящий' AND Status='Отвечен' AND Scheme='{i}'")
        number_of_accepted_calls = cur.fetchall()
        print(f"{i}")
        print(f"   Входящие - {number_of_calls[0][0]}")
        print(f"   Принятые - {number_of_accepted_calls[0][0]} ({round(number_of_accepted_calls[0][0]/number_of_calls[0][0]*100, 1)}%)")
        print(f"        Не принятые - {number_of_calls[0][0] - number_of_accepted_calls[0][0]} ({round((number_of_calls[0][0] - number_of_accepted_calls[0][0])/number_of_calls[0][0]*100, 1)}%)")
        
        for j in operators:
            cur.execute(f"SELECT COUNT(*) FROM calls WHERE Type='Входящий' AND Status='Отвечен' AND Scheme='{i}' AND Operator='{j}'")
            number_of_calls_by_operator = cur.fetchall()
            for k in number_of_calls_by_operator:
                if k[0] != 0:
                    print(f"        {j} - {k[0]} ({round(k[0]/number_of_calls[0][0]*100, 1)}%)")
                    #print(i, number_of_calls, number_of_accepted_calls, j, k[0])

        print("\n")

#outgoing calls
def outgoing_calls(conn):
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM calls WHERE Type='Исходящий'")
    outgoing = cur.fetchall()[0][0]
    print(f"Исходящие - {outgoing}")

    cur.execute("SELECT COUNT(*) FROM calls WHERE Type='Исходящий' AND Status='Отвечен'")
    accepted = cur.fetchall()[0][0]
    print(f"Отвеченные - {accepted} ({round(accepted/outgoing*100, 1)}%)")

    cur.execute("SELECT DISTINCT Origin FROM calls WHERE Type='Исходящий'")
    operators = cur.fetchall()

    calls = 0
    for i in operators:
        cur.execute(f"SELECT COUNT(*) FROM calls WHERE Type='Исходящий' AND Origin='{i[0]}'")
        calls = cur.fetchall()[0][0]
        cur.execute(f"SELECT COUNT(*) FROM calls WHERE Type='Исходящий' AND Status='Отвечен' AND Origin='{i[0]}'")
        accepted_calls = cur.fetchall()[0][0]
        print(f"    {i[0]} - {accepted_calls}/{calls} ({round(calls/outgoing*100, 1)}%)")


def main():
    database = "sipuni.db"

    conn = create_connection(database)
    with conn:
        #1. Total number of calls
        print('=================================================')
        total_number_of_calls = number_of_calls(conn)[0][0]
        print(f'Количество звонков = {total_number_of_calls}')
        print('\n')
        
        #2. Number of calls by type
        print("Принятые по типу")
        print('=================================================')
        a = all_calls(conn)
        for i in a:
            print(i, '=', a[i])
        print('\n')

        #3. Number of incoming calls by operator
        print("Принятые по опеаторам")
        print('=================================================')
        number_of_accepted_calls = 0
        operators = answered_calls_by_operator(conn)
        for i in operators:
            number_of_accepted_calls += operators[i]
            print(f"{i} = {operators[i]} ({round(operators[i]/a['Входящий']*100, 2)}%)")
        print("\n")
        
        print("Входящие")
        print('=================================================')
        print(f"    Принятые = {number_of_accepted_calls} ({round(number_of_accepted_calls/a['Входящий']*100, 2)}%)")
        print(f"    Пропущенные = {a['Входящий'] - number_of_accepted_calls} ({round((a['Входящий'] - number_of_accepted_calls)/a['Входящий']*100, 2)}%)")
        print("\n")

        #4. off hours incoming calls
        print("Время поступающих звонков")
        print('=================================================')
        timestamps = off_hours_calls(conn)
        #print(timestamps)
        hours = []
        for i in timestamps:
            hours.append(i.split()[1])
        
        working = 0
        off = 0
        for i in hours:
            if datetime.datetime.strptime(i, '%H:%M:%S') < datetime.datetime.strptime('20:00:00', '%H:%M:%S') and datetime.datetime.strptime(i, '%H:%M:%S') > datetime.datetime.strptime('08:00:00', '%H:%M:%S'):
                #print(datetime.datetime.strptime(i, '%H:%M:%S'))
                working += 1
            else:
                off += 1

        print(f"Входящие (рабочее время) = {working} ({round((working/(working+off)*100), 2)}%)")
        print(f"Входящие (нерабочее время) = {off} ({round((off/(working+off)*100), 2)}%)")
        print("\n")

        #5. Schemes
        print("Схемы")
        print('=================================================')
        call_destinations(conn)

        #6. Outgoing calls
        print('Исходящие')
        print('=================================================')
        outgoing_calls(conn)


if __name__=='__main__':
    main()