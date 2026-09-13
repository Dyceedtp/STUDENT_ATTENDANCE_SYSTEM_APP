import mysql.connector
from datetime import datetime

def log_attendance():
    print("--- Student Attendance Logging ---")
    student_id = input("Enter Student ID to check in: ").strip()

    if not student_id:
        print("[ERROR] Student ID cannot be empty.")
        return

    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="attendance_db"
        )
        cursor = conn.cursor()
        
        # Verify if student exists first
        cursor.execute("SELECT name FROM students WHERE student_id = %s", (student_id,))
        student = cursor.fetchone()
        
        if not student:
            print(f"[ERROR] Student ID '{student_id}' not found. Please register the student first.")
            return
            
        student_name = student[0]
        
        # Get current date and time
        now = datetime.now()
        current_date = now.strftime('%Y-%m-%d')
        current_time = now.strftime('%H:%M:%S')
        
        # Insert attendance record
        query = "INSERT INTO attendance (student_id, date, time) VALUES (%s, %s, %s)"
        cursor.execute(query, (student_id, current_date, current_time))
        conn.commit()
        
        print(f"[SUCCESS] Attendance logged for {student_name} ({student_id}) at {current_time} on {current_date}!")

    except mysql.connector.Error as err:
        print(f"[ERROR] Database error: {err}")
            
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'conn' in locals() and conn.is_connected():
            conn.close()

if __name__ == "__main__":
    log_attendance()