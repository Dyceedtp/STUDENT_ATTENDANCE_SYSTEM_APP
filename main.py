import subprocess
import sys

def main_menu():
    while True:
        print("\n==============================")
        print("  STUDENT ATTENDANCE SYSTEM   ")
        print("==============================")
        print("1. Register New Student")
        print("2. Log Attendance")
        print("3. Exit")
        
        choice = input("Select an option (1-3): ").strip()
        
        if choice == '1':
            print("\n--- Launching Registration ---")
            subprocess.run([sys.executable, "register_student.py"])
        elif choice == '2':
            print("\n--- Launching Attendance Log ---")
            subprocess.run([sys.executable, "log_attendance.py"])
        elif choice == '3':
            print("\nExiting system. Goodbye!")
            break
        else:
            print("[ERROR] Invalid choice. Please enter 1, 2, or 3.")

if __name__ == "__main__":
    main_menu()