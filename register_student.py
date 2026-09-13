import mysql.connector

def register_student():
    print("--- Student Registration System ---")
    student_id = input("Enter Student ID (e.g., STU001): ").strip()
    student_name = input("Enter Student Name: ").strip()

    if not student_id or not student_name:
        print("[ERROR] Student ID and Name cannot be empty.")
        return

    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="attendance_db"
        )
        cursor = conn.cursor()
        
        query = "INSERT INTO students (student_id, name) VALUES (%s, %s)"
        cursor.execute(query, (student_id, student_name))
        conn.commit()
        
        print(f"[SUCCESS] Student {student_name} ({student_id}) registered successfully!")

    except mysql.connector.Error as err:
        if err.errno == 1062:
            print(f"[ERROR] Student ID '{student_id}' already exists.")
        else:
            print(f"[ERROR] Database error: {err}")
            
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'conn' in locals() and conn.is_connected():
            conn.close()

if __name__ == "__main__":
    register_student()