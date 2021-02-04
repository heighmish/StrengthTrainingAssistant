from Modules.speechRecognition.speechRecognitionFunction import *
from Modules.Database.DbConnection import *
import sqlite3
import json
import sys
import math


#For queries that actually update or change the data, use the validate and commit function

class TrainingSession:
    def __init__(self):
        self.connection, self.cursor = InitCursor()
        self.getCurrentProgram()
        self.getWeekandDay()
        self.getSetId()
        self.daySynopsis()
        self.listen()
        self.connection.close()

    def getCurrentProgram(self):
        with open("Modules\Database\settings.json", "r") as read_file:
            data = json.load(read_file)
        self.ProgramName = data["currentProgram"]
        self.daysPerWeek = data["daysPerWeek"]
        text = f"Your current program is {self.ProgramName}"
        text_to_Speech(text)
        self.cursor.execute("SELECT P_id FROM programs WHERE P_name = ?;", (self.ProgramName,))
        self.P_id = (self.cursor.fetchone())[0]
        print(self.ProgramName, self.P_id)

    def getWeekandDay(self):
        self.cursor.execute("SELECT min(Week_num) FROM program_weeks WHERE program_weeks.P_id = ? AND program_weeks.Week_complete = 0;", (self.P_id,))
        self.WeekNum = (self.cursor.fetchone())[0]
        self.cursor.execute("SELECT min(Day_num) FROM program_weeks, program_days \
            WHERE program_weeks.Pw_id = program_days.Pw_id AND program_days.P_id = ? \
            AND program_weeks.Week_Num = ? AND program_days.Day_complete = 0;", (self.P_id, self.WeekNum,))
        self.DayNum = (self.cursor.fetchone())[0]
        self.todaysTable = self.ProgramName + (str(self.WeekNum) + str(self.DayNum))
        self.previousWeekTable = self.ProgramName + (str(self.WeekNum-1) + str(self.DayNum))
        text_to_Speech(f"Today is Week {self.WeekNum}, day {self.DayNum}")
        print(self.DayNum, self.WeekNum)
        print(self.todaysTable)

    def getSetId(self):
        self.cursor.execute(f"SELECT min(Set_id) from {self.todaysTable} WHERE Time is NULL;") #time is used as to allow skipped sets to record data as null
        self.setId = (self.cursor.fetchone())[0]
        print(self.cursor.fetchone)
        print(self.setId)

    def daySynopsis(self):
        #Gives an overview of the days workout
        self.cursor.execute(f"SELECT Movement, count(Movement), E_reps from {self.todaysTable} WHERE Set_id > {self.setId-1} GROUP BY Movement;")
        Synopsis = self.cursor.fetchall()
        #Text to speech
        for movement in Synopsis:
            decomp = str(movement).split(",")
            if int(decomp[1]) > 1:
                string = f"{decomp[0]}, {decomp[1]} sets of {decomp[2]}."
            else:
                string = f"{decomp[0]}, {decomp[1]} set of {decomp[2]}."
            text_to_Speech(string)
        self.getCurrentSet()
        

    def recordSet(self):
        #UPDATE SQL query increase set counter if successful
        #Listen and get the data
        weight, reps, rpe = self.getSetValues()
        try:
            oneRm = getOneRM(weight, reps, rpe)
        except: 
            oneRm = None
        Query = f"UPDATE {self.todaysTable} SET A_reps = {reps}, A_rpe = {rpe}, Weight_= {weight}, est_1rm = {oneRm}, Time = CURRENT_TIMESTAMP WHERE set_id = {self.setId};"
        self.cursor.execute(Query)
        if self.validateAndCommit() == True:
            self.setId += 1
            text_to_Speech("Command executed successfully.")
            self.getCurrentSet()
        else:
            text_to_Speech("Command failed to be entered into the database.")
        
    def getSetValues(self):
        while True:
            print("Enter weight, reps, rpe")
            weight, reps, rpe = short_Command("Weight"), short_Command("reps"), short_Command("rpe")
            print(weight,reps,rpe)
            text_to_Speech(f"{weight} kg, {reps} reps, for rpe {rpe}")
            if short_Command("Is this correct?") == 'yes':
                return weight, reps, rpe
            else:
                print("Please try again.")

    def getCurrentSet(self):
        Query = f"SELECT * FROM {self.todaysTable} WHERE Set_id = {self.setId};"
        self.cursor.execute(Query)
        movement = list(self.cursor.fetchone())
        if movement[5].is_integer():
            if self.setId == 1:
                text = f"Your first set today is {movement[3]}, {movement[4]} reps at rpe {movement[5]}."
            else:
                text = f"The current set is {movement[3]}, {movement[4]} reps at rpe {movement[5]}."
        else:
            rpeSplit = list(math.modf(movement[5]))
            print(rpeSplit, '\n', movement)
            if rpeSplit[1] == 1: #1 indicates backoff from top set
                print(f"SELECT Weight_ FROM {self.todaysTable} WHERE Movement = {movement[3]} AND E_rpe = (SELECT MAX(E_rpe) from {self.todaysTable} WHERE Movement = {movement[3]});")
                self.cursor.execute(f'SELECT Weight_ FROM {self.todaysTable} WHERE Movement = "{movement[3]}" AND E_rpe = (SELECT MAX(E_rpe) from {self.todaysTable} WHERE Movement = "{movement[3]}");')
                maxRpeSetWeight = list(self.cursor.fetchone())[0]
                backOffSetWeight = round(maxRpeSetWeight * rpeSplit[0], 1)
                text = f"The current set is {movement[3]}, {movement[4]} reps at {backOffSetWeight} kgs"
                print('backOffSetWeight:', backOffSetWeight)
            elif rpeSplit[1] == 2: #percentage of 1rm
                self.cursor.execute(f'SELECT MAX(est_1rm) FROM {self.todaysTable} WHERE Movement = "{movement[3]}";')
                maxEst1rmWeight = list(self.cursor.fetchone())[0]
                percentMax1Rm = round(maxEst1rmWeight * rpeSplit[0], 1)
                text = f"The current set is {movement[3]}, {movement[4]} reps at {percentMax1Rm} kgs"
        text_to_Speech(text)
    
    def getPreviousWeekMax(self):
        #Returns highest weight lifted for the current exercise for the previous week
        if self.WeekNum == 1:
            text_to_Speech("There is no previous week.")
            return
        else:
            try:
                self.cursor.execute(f"SELECT * FROM {self.todaysTable} WHERE Set_id = {self.setId};")
                movement = list(self.cursor.fetchone())
                movementName = movement[3]
                self.cursor.execute(f'SELECT MAX(Weight_), A_rpe FROM {self.previousWeekTable} WHERE Movement = "{movementName}"')
            except:
                print("No comparable exercise")
                return 
    
    def skipSet(self):
        #Voice command
        #Insert series of Null values into the dataframe rather than leave blank  
        #Very similar to recordSet function
        Query = f"UPDATE {self.todaysTable} SET A_reps = Null, A_rpe = Null, Weight_= Null, est_1rm = Null, Time = CURRENT_TIMESTAMP WHERE set_id = {self.setId};"
        self.cursor.execute(Query)
        if self.validateAndCommit() == True:
            self.setId += 1
            text_to_Speech("Set sucessfully skipped.")
            self.getCurrentSet()
        else:
            text_to_Speech("Failure to skip set.")

    def addSet(self):
        #Get voice command maybe ("Add current __kg __reps __rpe") either weight here or additional line test which does better
        #INSERT query
        movement = short_Command("What exercise?")
        weight, reps, rpe = self.getSetValues()
        oneRM = getOneRM(weight, reps, rpe)
        Query = f"INSERT INTO {self.todaysTable} (Movement, Weight, A_reps, A_rpe, est_1rm Time) VALUES ({movement}, {weight}, {reps}, {rpe}, {oneRM}, CURRENT_TIMESTAMP);"
        self.cursor.execute(Query)
        if self.validateAndCommit() == True:
            text_to_Speech("Set sucessfully added") #surely this works, that adding a set affects one row
            self.getCurrentSet()
        else:
            text_to_Speech("Failure to add set.")
        

    def endSession(self):
        #update completion for the day
        DayQuery = f"UPDATE program_days SET Day_complete = 1 WHERE Week_num = {self.WeekNum} AND Day_num = {self.DayNum} AND P_id={self.P_id};"
        #execute and validate
        self.cursor.execute(DayQuery)
        if self.validateAndCommit() == True:
            print("Day logged")
            text_to_Speech("Day sucessfully logged.")
            #maybe some analysis
        else:
            print("Day not logged")
            text_to_Speech("Failure to log day")
        #check if this is last day of the week if it is then update the program_weeks complete
        if self.DayNum == self.daysPerWeek: #last day of the week
            WeekQuery = f"UPDATE program_weeks SET Week_complete = 1 WHERE P_id = {self.P_id} AND Week_num = {self.WeekNum};"
            self.cursor.execute(WeekQuery)
            if self.validateAndCommit() == True:
                print("Week logged")
                text_to_Speech("Week sucessfully logged.")
                #maybe some analysis
            else:
                print("Week failed to be logged")
                text_to_Speech("Failure to log day")
        self.connection.close()
        sys.exit()

    def listen(self):
        while True:
            if always_listening() == True:
                #Activate ask for new command
                command = short_Command()
                #Pass the command to be directed for functionality
                self.directCommand(command)
                

    def directCommand(self, command):
        print("Command received", command)
        if type(command) == None:
            print("Command not received")
            return 
        if "record" in command:
            self.recordSet()
        elif "current" in command:
            self.getCurrentSet()
        elif "skip" in command:
            self.skipSet()
        elif "add" in command:
            self.addSet()
        elif "what's left" in command or "synopsis" in command:
            self.daySynopsis()
        elif "help" in command:
            self.help()
        elif "rpe" in command:
            self.rpeHelp()
        elif "previous" in command:
            self.getPreviousWeekMax()
        elif "end" in command:
            self.endSession()

    def changeProgram(self):
        pass
    
    def help(self):
        #list of commands and functionality
        pass
    
    def rpeHelp(self):
        text = "Rpe 6 is a light easy warmup, more than 4 reps left. Rpe 7 is 3 more reps left. Rpe 8, 2 more reps. Rpe 9, 1 more rep. Rpe 10, a true maximum full exertion."
        text_to_Speech(text)

    def validateAndCommit(self):
        #Check if statement executed successfully, then commits transaction.
        count = self.cursor.rowcount
        if count == -1: #cursor did not execute correctly.
            return False
        elif count > 0:
            self.connection.commit()
            return True

def getOneRM(weight, reps, rpe):
    OneRM_dict = {1: {10: 100, 9.5: 97.8, 9: 95.5, 8.5: 93.9 ,8: 92.9, 7.5: 90.7, 7: 89.2, 6.5: 87.8, 6: 86.3},
        2:{10: 95.5, 9.5: 93.9 ,9: 92.2, 8.5: 90.7, 8: 89.2, 7.5: 87.8, 7: 86.3, 6.5: 85, 6: 83.7},
        3:{10: 92.2, 9.5: 90.7, 9: 89.2, 8.5: 87.8,8: 86.3, 7.5: 85, 7: 83.7, 6.5: 82.4, 6: 81.1},
        4:{10: 89.2, 9.5: 87.8, 9: 86.3, 8.5: 85,8: 83.7, 7.5: 82.4, 7: 81.1, 6.5: 79.9, 6: 78.6},
        5:{10: 86.3, 9.5: 85, 9: 83.7, 8.5: 82.4,8: 81.1, 7.5: 79.9, 7: 78.6, 6.5: 77.4, 6: 76.2},
        6:{10: 83.7, 9.5: 82.4, 9: 81.1, 8.5: 79.9,8: 78.6, 7.5: 77.4, 7: 76.2, 6.5: 75.1, 6: 73.9},
        7:{10: 81.1, 9.5:79.9, 9:78.6, 8.5:77.4,8:76.2, 7.5:75.1, 7:73.9, 6.5:72.3, 6: 70.7},
        8:{10: 78.6, 9.5:77.4, 9:76.2, 8.5:75.1,8:73.9, 7.5:72.3, 7:70.7, 6.5:69.4, 6: 68},
        9:{10: 76.2, 9.5:75.1, 9:73.9, 8.5:72.3,8:70.7, 7.5:69.4, 7:68, 6.5:66.7, 6: 65.3},
        10:{10: 73.9, 9.5:72.3, 9:70.7, 8.5:69.4,8:68, 7.5:66.7, 7:65.3, 6.5:64, 6: 62.6},
        11:{10: 70.7, 9.5:69.4, 9:68, 8.5:66.7,8:65.3, 7.5:64, 7:62.6, 6.5:61.3, 6: 59.9},
        12:{10: 68, 9.5:66.7, 9:65.3, 8.5:64,8:62.6, 7.5:61.3, 7:59.9, 6.5:58.6, 6: 57.4}}
    return ((float(weight)/OneRM_dict[int(reps)][float(rpe)]) * 100)




print(sys.version)
A = TrainingSession()
#A.recordSet()