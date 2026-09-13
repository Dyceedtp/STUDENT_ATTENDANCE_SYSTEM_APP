import streamlit as st
import mysql.connector

# Page Configuration
st.set_page_config(
    page_title="Intelligent Student Attendance System",
    page_icon="🎓",
    layout="wide"
)

# Aiven MySQL Database Connection
def get_db_connection():
    return mysql.connector.connect(
        host="your_aiven_host",
        user="your_db_user",
        password="your_db_password",
        database="your_database_name",
        port=3306
    )

# Sidebar Navigation matching your live app
st.sidebar.title("Polytechnic")
st.sidebar.caption("INTELLIGENT ATTENDANCE v2.0")
menu = st.sidebar.radio("Navigation", ["Dashboard", "Registration", "Live Capture", "Session Reports"])

if menu == "Dashboard":
    st.title("Admin Dashboard")
    st.write("Welcome to the Intelligent Student Attendance System dashboard.")

elif menu == "Registration":
    st.title("Student Registration Portal")
    st.write("Register new students, view the roster, or delete individual student records.")
    
    # Registration Form matching your screenshot layout
    with st.form("registration_form"):
        student_id = st.text_input("Student ID (e.g., STU002)")
        full_name = st.text_input("Full Name")
        
        submit_button = st.form_submit_button("Register Student")

        if submit_button:
            if student_id and full_name:
                try:
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    
                    # Insert into database (adjust column names to match your table)
                    query = "INSERT INTO students (student_id, full_name) VALUES (%s, %s)"
                    cursor.execute(query, (student_id, full_name))
                    conn.commit()
                    
                    cursor.close()
                    conn.close()
                    
                    st.success(f"Successfully registered {full_name} (ID: {student_id})!")
                except Exception as e:
                    st.error(f"Database Error: {e}")
            else:
                st.warning("Please fill in both Student ID and Full Name.")

    # Currently Registered Students Section
    st.markdown("---")
    st.subheader("Currently Registered Students")
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT student_id, full_name FROM students")
        students = cursor.fetchall()
        cursor.close()
        conn.close()
        
        if students:
            for s in students:
                st.text(f"ID: {s[0]} | Name: {s[1]}")
        else:
            st.info("No students registered yet.")
    except Exception as e:
        st.write("Unable to load student roster at the moment.")

elif menu == "Live Capture":
    st.title("Real-Time Attendance Capture")
    st.info("Live camera stream and face recognition logic will execute here.")

elif menu == "Session Reports":
    st.title("Session Reports")
    st.write("Attendance logs and analytics reports.")

# Logout button at the bottom of the sidebar
if st.sidebar.button("Logout"):
    st.sidebar.success("Logged out successfully.")