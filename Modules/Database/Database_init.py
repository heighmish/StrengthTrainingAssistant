import sqlite3
#Creates the initial database including, program, program weeks and program days.

def init_database():
    conn = sqlite3.connect('Main_Database.db')
    cur = conn.cursor()
    temp = open('schema.sql')
    basic_schema = temp.read()
    temp.close()
    try:
        cur.executescript(basic_schema)
    except:
        print("Exception.")
    conn.close()

init_database()

#cur.execute('INSERT INTO programs (P_name) Values ("BBM_beg"),("BBM_str");')
#data = cur.execute('SELECT * from program_weeks;')
#for item in data:
    #print(item)

