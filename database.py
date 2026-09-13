import mysql.connector

try:
    db = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="attendance_db"
    )
    print("Successfully connected to attendance_db!")
    db.close()
except Exception as err:
    print(f"Error connecting to database: {err}")