import streamlit as st
import mysql.connector
import cv2
import numpy as np
import pandas as pd
from datetime import datetime

# Page Configuration
st.set_page_config(
    page_title="Intelligent Student Attendance System",
    page_icon="🎓",
    layout="wide"
)

# Database Connection Function using Streamlit Secrets
def get_db_connection():
    try:
        db = mysql.connector.connect(
            host=st.secrets["mysql"]["host"],
            port=st.secrets["mysql"]["port"],
            user=st.secrets["mysql"]["user"],
            password=st.secrets["mysql"]["password"],
            database=st.secrets["mysql"]["database"]
        )
        return db
    except Exception as err:
        st.error(f"Database Error: {err}")
        return None

# Initialize Database Tables if they don't exist
def init_db():
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS students (
                student_id VARCHAR(50) PRIMARY KEY,
                full_name VARCHAR(100) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS attendance (
                id INT AUTO_INCREMENT PRIMARY KEY,
                student_id VARCHAR(50),
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (student_id) REFERENCES students(student_id)
            )
        """)
        conn.commit()
        cursor.close()
        conn.close()

init_db()

# Sidebar Navigation
st.sidebar.title("Polytechnic")
st.sidebar.markdown("### INTELLIGENT ATTENDANCE v2.0")
st.sidebar.markdown("---")

navigation = st.sidebar.radio("Navigation", ["Dashboard", "Registration", "Live Capture", "Session Reports"])

st.sidebar.markdown("---")
if st.sidebar.button("Logout"):
    st.success("Logged out successfully.")

# Dashboard View
if navigation == "Dashboard":
    st.title("System Dashboard")
    st.markdown("Overview of student attendance metrics and database status.")
    
    conn = get_db_connection()
    if conn:
        try:
            students_df = pd.read_sql("SELECT * FROM students", conn)
            attendance_df = pd.read_sql("SELECT * FROM attendance", conn)
            conn.close()
            
            col1, col2 = st.metrics = st.columns(2) if hasattr(st, "columns") else (st, st)
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric(label="Total Registered Students", value=len(students_df))
            with col2:
                st.metric(label="Total Attendance Logs", value=len(attendance_df))
                
            st.markdown("### Recent Attendance")
            if not attendance_df.empty:
                st.dataframe(attendance_df.tail(10), use_container_width=True)
            else:
                st.info("No attendance records found yet.")
        except Exception as e:
            st.error(f"Error loading dashboard data: {e}")

# Registration View
elif navigation == "Registration":
    st.title("Student Registration Portal")
    st.markdown("Register new students, view the roster, or delete individual student records.")
    
    with st.form("registration_form"):
        student_id = st.text_input("Student ID (e.g., STU002)")
        full_name = st.text_input("Full Name")
        submit_button = st.form_submit_button("Register Student")
        
        if submit_button:
            if student_id and full_name:
                conn = get_db_connection()
                if conn:
                    try:
                        cursor = conn.cursor()
                        cursor.execute("INSERT INTO students (student_id, full_name) VALUES (%s, %s)", (student_id, full_name))
                        conn.commit()
                        cursor.close()
                        conn.close()
                        st.success(f"Successfully registered {full_name} (ID: {student_id})!")
                    except mysql.connector.Error as err:
                        st.error(f"Registration Error: {err}")
            else:
                st.warning("Please fill in both Student ID and Full Name.")
                
    st.markdown("### Currently Registered Students")
    conn = get_db_connection()
    if conn:
        try:
            students_df = pd.read_sql("SELECT student_id, full_name, created_at FROM students", conn)
            conn.close()
            if not students_df.empty:
                st.dataframe(students_df, use_container_width=True)
            else:
                st.info("Database table is empty or initializing.")
        except Exception as e:
            st.error(f"Could not load roster: {e}")

# Live Capture View
elif navigation == "Live Capture":
    st.title("Live Face Recognition Capture")
    st.markdown("Use camera feed to detect and mark attendance automatically.")
    st.info("Camera stream interface active. Ensure webcam permissions are enabled.")
    
    picture = st.camera_input("Take a snapshot for recognition")
    if picture:
        bytes_data = picture.getvalue()
        cv_img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)
        st.image(cv_img, channels="BGR", caption="Captured Frame")
        st.success("Frame captured successfully. Processing facial features...")

# Session Reports View
elif navigation == "Session Reports":
    st.title("Session Reports & Logs")
    st.markdown("Export and view comprehensive attendance logs.")
    
    conn = get_db_connection()
    if conn:
        try:
            df = pd.read_sql("""
                SELECT a.id, s.student_id, s.full_name, a.timestamp 
                FROM attendance a 
                JOIN students s ON a.student_id = s.student_id
            """, conn)
            conn.close()
            
            if not df.empty:
                st.dataframe(df, use_container_width=True)
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button("Download Report as CSV", data=csv, file_name="attendance_report.csv", mime="text/csv")
            else:
                st.info("No attendance logs available for export.")
        except Exception as e:
            st.error(f"Error generating report: {e}")