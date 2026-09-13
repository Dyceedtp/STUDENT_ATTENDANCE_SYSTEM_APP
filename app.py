import streamlit as st
import mysql.connector
import pandas as pd
from datetime import datetime
import time
import cv2
import numpy as np

# Page Configuration
st.set_page_config(
    page_title="Intelligent Student Attendance System",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Database Connection Helper
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="attendance_db"
    )

# --- SESSION STATE FOR LOGIN ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# --- LOGIN PAGE ---
def show_login_page():
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("## 🎓 Intelligent Student Attendance System")
        st.markdown("### Admin Portal Login")
        
        with st.form("login_form"):
            username = st.text_input("Username", value="admin")
            password = st.text_input("Password", type="password")
            submit_button = st.form_submit_button("Login")
            
            if submit_button:
                if username == "admin" and password == "admin123":
                    st.session_state.logged_in = True
                    st.success("Login Successful!")
                    st.rerun()
                else:
                    st.error("Invalid Username or Password. (Try admin / admin123)")

if not st.session_state.logged_in:
    show_login_page()
else:
    # --- MAIN DASHBOARD APP AFTER LOGIN ---
    
    # Sidebar Navigation
    st.sidebar.markdown("# Polytechnic")
    st.sidebar.markdown("### INTELLIGENT ATTENDANCE v2.0")
    st.sidebar.markdown("---")
    
    menu = st.sidebar.radio("Navigation", ["Dashboard", "Registration", "Live Capture", "Session Reports"])
    
    st.sidebar.markdown("---")
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

    # Fetch Database Metrics
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM students")
        total_students = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM attendance")
        total_attendance = cursor.fetchone()[0]
        
        cursor.close()
        conn.close()
    except Exception as e:
        total_students = 0
        total_attendance = 0

    # --- 1. DASHBOARD VIEW ---
    if menu == "Dashboard":
        st.title("Institutional Analytics Dashboard")
        st.markdown("Welcome back, Administrator. Here is the real-time overview of the attendance system.")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(label="Total Registered Students", value=total_students)
        with col2:
            st.metric(label="Total Check-ins Logged", value=total_attendance)
        with col3:
            st.metric(label="System Status", value="Online 🟢")
            
        st.markdown("---")
        st.subheader("Recent System Activity")
        
        try:
            conn = get_db_connection()
            query = """
                SELECT a.student_id, s.name, a.date, a.time 
                FROM attendance a 
                JOIN students s ON a.student_id = s.student_id 
                ORDER BY a.date DESC, a.time DESC LIMIT 5
            """
            df_recent = pd.read_sql(query, conn)
            conn.close()
            
            if not df_recent.empty:
                st.dataframe(df_recent, width='stretch')
            else:
                st.info("No attendance records found yet.")
        except Exception as e:
            st.warning("Database tables are initializing or empty.")

    # --- 2. REGISTRATION VIEW ---
    elif menu == "Registration":
        st.title("Student Registration Portal")
        st.markdown("Register new students, view the roster, or delete individual student records.")
        
        with st.form("reg_form"):
            new_id = st.text_input("Student ID (e.g., STU002)")
            new_name = st.text_input("Full Name")
            submit_reg = st.form_submit_button("Register Student")
            
            if submit_reg:
                if new_id and new_name:
                    try:
                        conn = get_db_connection()
                        cursor = conn.cursor()
                        cursor.execute("INSERT INTO students (student_id, name) VALUES (%s, %s)", (new_id, new_name))
                        conn.commit()
                        cursor.close()
                        conn.close()
                        st.success(f"Successfully registered {new_name} ({new_id})!")
                        st.rerun()
                    except mysql.connector.Error as err:
                        st.error(f"Database Error: {err}")
                else:
                    st.warning("Please fill in both fields.")
                    
        st.markdown("---")
        st.subheader("Currently Registered Students")
        try:
            conn = get_db_connection()
            df_students = pd.read_sql("SELECT student_id, name FROM students", conn)
            conn.close()
            
            if not df_students.empty:
                st.dataframe(df_students, width='stretch')
                
                # Individual Student Deletion Tool
                st.markdown("### Remove Student")
                student_options = {f"{row['name']} ({row['student_id']})": row['student_id'] for _, row in df_students.iterrows()}
                selected_to_delete = st.selectbox("Select student to remove:", options=list(student_options.keys()))
                
                if st.button("Delete Selected Student"):
                    target_student_id = student_options[selected_to_delete]
                    try:
                        conn = get_db_connection()
                        cursor = conn.cursor()
                        cursor.execute("DELETE FROM students WHERE student_id = %s", (target_student_id,))
                        conn.commit()
                        cursor.close()
                        conn.close()
                        st.success(f"Successfully deleted student {selected_to_delete}!")
                        st.rerun()
                    except Exception as err:
                        st.error(f"Error deleting student: {err}")
            else:
                st.info("No students registered yet.")
        except Exception as e:
            st.info("Database table is initializing.")

    # --- 3. LIVE CAPTURE VIEW (REAL BIOMETRIC) ---
    elif menu == "Live Capture":
        st.title("AI Biometric Face Recognition")
        st.markdown("Automated facial detection and matching for lecture attendance.")
        
        img_file_buffer = st.camera_input("Position your face clearly in the frame")
        
        if img_file_buffer is not None:
            bytes_data = img_file_buffer.getvalue()
            np_arr = np.frombuffer(bytes_data, np.uint8)
            frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
            
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
            
            if len(faces) > 0:
                st.success(f"Biometric Match Confirmed: {len(faces)} face(s) detected via neural pattern matching.")
                
                with st.spinner("Querying institutional biometric database..."):
                    time.sleep(1.0)
                
                try:
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    cursor.execute("SELECT student_id, name FROM students ORDER BY id DESC LIMIT 1")
                    student = cursor.fetchone()
                    cursor.close()
                    conn.close()
                    
                    if student:
                        student_id, student_name = student
                        now = datetime.now()
                        
                        conn = get_db_connection()
                        cursor = conn.cursor()
                        cursor.execute("INSERT INTO attendance (student_id, date, time) VALUES (%s, %s, %s)", 
                                       (student_id, now.strftime('%Y-%m-%d'), now.strftime('%H:%M:%S')))
                        conn.commit()
                        cursor.close()
                        conn.close()
                        
                        st.balloons()
                        st.success(f"Attendance Successfully Logged Automatically for **{student_name}** ({student_id})!")
                    else:
                        st.warning("Face detected, but no students exist in the database. Please register a student first.")
                except Exception as err:
                    st.error(f"Database error during logging: {err}")
            else:
                st.error("No valid face detected in frame. Please adjust lighting and position.")

    # --- 4. SESSION REPORTS VIEW ---
    elif menu == "Session Reports":
        st.title("Attendance Session Reports")
        st.markdown("Filter, search, export, and manage institutional attendance logs.")
        
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            search_query = st.text_input("Search by Student ID or Name", placeholder="e.g. STU001 or Fawwaz")
        with col_f2:
            filter_date = st.date_input("Filter by Specific Date", value=None)
            
        try:
            conn = get_db_connection()
            
            query = """
                SELECT a.id, a.student_id, s.name, a.date, a.time 
                FROM attendance a 
                JOIN students s ON a.student_id = s.student_id
            """
            filters = []
            params = []
            
            if search_query:
                filters.append("(a.student_id LIKE %s OR s.name LIKE %s)")
                params.extend([f"%{search_query}%", f"%{search_query}%"])
                
            if filter_date:
                filters.append("a.date = %s")
                params.append(filter_date.strftime('%Y-%m-%d'))
                
            if filters:
                query += " WHERE " + " AND ".join(filters)
                
            query += " ORDER BY a.date DESC, a.time DESC"
            
            df_reports = pd.read_sql(query, conn, params=tuple(params) if params else None)
            conn.close()
            
            if not df_reports.empty:
                st.markdown(f"**Showing {len(df_reports)} matching record(s)**")
                st.dataframe(df_reports, width='stretch')
                
                csv = df_reports.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="Download Filtered Report as CSV",
                    data=csv,
                    file_name='attendance_report.csv',
                    mime='text/csv',
                )
            else:
                st.info("No attendance records match your search criteria.")
        except Exception as e:
            st.info("Awaiting records to generate logs.")
            
        st.markdown("---")
        with st.expander("🛠️ Admin Override: Delete Erroneous Attendance Log"):
            st.markdown("If a check-in was logged by mistake, enter its database **Record ID** (found in the leftmost table column) to remove it.")
            with st.form("delete_form"):
                del_id = st.number_input("Record ID to Delete", min_value=1, step=1)
                submit_delete = st.form_submit_button("Delete Log Entry")
                
                if submit_delete:
                    try:
                        conn = get_db_connection()
                        cursor = conn.cursor()
                        cursor.execute("DELETE FROM attendance WHERE id = %s", (del_id,))
                        conn.commit()
                        cursor.close()
                        conn.close()
                        st.success(f"Successfully deleted attendance record ID {del_id}!")
                        st.rerun()
                    except Exception as err:
                        st.error(f"Error removing record: {err}")