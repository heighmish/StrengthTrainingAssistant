import sqlite3

def InitCursor():
    connection = sqlite3.connect('Main_Database.db')
    cursor = connection.cursor()
    connection.commit()