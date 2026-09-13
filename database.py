import mysql.connector

try:
    db = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="attendance_db"
    )
    
    if db.is_connected():
        print("Successfully connected to attendance_db!")
        
    db.close()

except mysql.connector.Error as err:
    print(f"Error connecting to database: {err}")