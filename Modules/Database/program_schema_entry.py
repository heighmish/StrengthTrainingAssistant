import sqlite3
import os

def init_database():
    conn = sqlite3.connect('Main_Database.db')
    cur = conn.cursor()
    temp = open('Modules\Database\schema.sql')
    basic_schema = temp.read()
    temp.close()
    try:
        cur.executescript(basic_schema)
    except Exception as e:
        print("Error creating the basic schema of the database.", e)
    conn.close()

init_database()

class Program:
    def __init__(self, dir_name, week_num, days_per_week):
        self.name = (dir_name.split('\\'))[-1]
        self.dir_name = dir_name
        self.week_num = week_num
        self.days_per_week = days_per_week
        self.connection = sqlite3.connect('Main_Database.db')
        self.cursor = self.connection.cursor()
        self.enter_program_id()
        self.enter_program_weeks()
        self.connection.commit()

    def enter_program_id(self):
        try:
            self.program_insert_string = "INSERT INTO programs (P_name) VALUES (?);"
            self.cursor.execute(self.program_insert_string, (self.name,))
        except:
            pass
        self.cursor.execute("SELECT P_id FROM programs where P_name = ?;", (self.name,))
        self.P_id = (self.cursor.fetchone())[0]
    
    def enter_program_weeks(self):
        #try:
        self.week_insert_string = "INSERT INTO program_weeks (P_id, Week_num) VALUES (?, ?);"
        temp = open('Modules\Database\Temp_file.sql')
        create_table_temp = temp.read()
        create_table_string = "CREATE TABLE IF NOT EXISTS "
        temp.close()
        self.training_number = 1
        self.training_data = open(self.dir_name).readlines() #reads the .txt file containing training program
        for i in range(1, self.week_num+1):
            self.cursor.execute(self.week_insert_string, (self.P_id, i,)) #inserts weeks into DB
            for j in range(1, self.days_per_week+1):
                self.program_days_insert_string = "INSERT INTO program_days (Pw_id, Day_num, P_id) VALUES (?, ?, ?);"
                self.cursor.execute(self.program_days_insert_string, (i, j, self.P_id,))
                self.cursor.execute("SELECT Pd_id FROM program_days WHERE Pw_id= ? AND Day_num = ?;", (i, j,))
                self.training_id = (self.cursor.fetchone())[0]
                #Create individual table
                table_name = self.name + (str(i)+str(j))
                create_table_final = create_table_string + table_name + create_table_temp
                print(create_table_final)
                self.cursor.execute(create_table_final)
                #read data from the file there will be 36 rows, do week * day
                self.training_data_temp = self.training_data[self.training_number-1] #gets the training data required for given day
                insert_statement = "INSERT INTO " + table_name + "(Movement, E_reps, E_rpe, Pd_id) VALUES (?, ?, ?, ?);"
                daily_training_data = self.training_data_temp.split(";") #might be wrong ahhh
                for k in daily_training_data:
                    temp = k.split(",")
                    movement = temp[0].lstrip()
                    for l in range(1,len(temp),2):
                        rep_temp = temp[l]
                        rpe_temp = temp[l+1]
                        self.cursor.execute(insert_statement, (movement, rep_temp, rpe_temp, self.training_id,))
                        self.connection.commit()

                
                
                self.training_number  += 1
        #except:
            #self.connection.commit()


#BBM_Beg = Program('Modules\Database\Programs\BBM_Beg', 12, 3)
#BBM_Str2 = Program('Modules\Database\Programs\BBM_Str2', 12, 3)
#temp = Program('Modules\Database\Programs\\temp', 1, 1)