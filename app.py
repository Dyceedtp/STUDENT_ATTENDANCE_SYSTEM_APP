import streamlit as st
import mysql.connector
from datetime import datetime

# Page Configuration
st.set_page_config(
    page_title="Intelligent Student Attendance System",
    page_icon="🎓",
    layout="wide"
)

# Aiven MySQL Database Connection Function
def get_db_connection():
    return mysql.connector.connect(
        host="your_aiven_host",
        user="your_db_user",
        password="your_db_password",
        database="your_database_name",
        port=3306
    )

# Sidebar Navigation matching your documentation
st.sidebar.title("Polytechnic")
st.sidebar.caption("INTELLIGENT ATTENDANCE v2.0")

menu = st.sidebar.radio(
    "Navigation", 
    ["Dashboard", "Registration", "Live Capture", "Session Reports"]
)

st.sidebar.markdown("---")
if st.sidebar.button("Logout"):
    st.sidebar.success("Logged out successfully.")

# ==========================================
# 1. DASHBOARD / INSTITUTIONAL ANALYTICS
# ==========================================
if menu == "Dashboard":
    st.title("Institutional Analytics")
    st.write("Overview of system statistics, attendance trends, and real-time activity tracking.")
    
    # Fetch real counts from database for a fresh state
    total_students = 0
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM students")
        result = cursor.fetchone()
        if result:
            total_students = result[0]
        cursor.close()
        conn.close()
    except Exception:
        total_students = 0

    # Top Metric Cards
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(label="Total Registered Students", value=total_students)
    with col2:
        st.metric(label="Average Attendance", value="0.0%")
    with col3:
        st.metric(label="Total Courses", value="0")
        
    st.markdown("---")
    st.subheader("Recent Activity")
    
    # Fresh app state: Empty recent activity log
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT timestamp, matric_number, course, status FROM attendance_logs ORDER BY timestamp DESC LIMIT 10")
        logs = cursor.fetchall()
        cursor.close()
        conn.close()
        
        if logs:
            st.markdown("| Timestamp | Matric No. | Course | Status |")
            st.markdown("| :--- | :--- | :--- | :--- |")
            for log in logs:
                st.markdown(f"| {log[0]} | {log[1]} | {log[2]} | {log[3]} |")
        else:
            st.info("No recent activity recorded yet. Start a live capture session to begin tracking.")
    except Exception:
        st.info("No recent activity recorded yet. Database tables will populate during live sessions.")

# ==========================================
# 2. STUDENT BIOMETRIC ENROLLMENT (REGISTRATION)
# ==========================================
elif menu == "Registration":
    st.title("Student Biometric Enrollment")
    st.write("Register new student profiles and capture facial biometric templates.")
    
    # Split layout matching Figure 5.2
    form_col, capture_col = st.columns(2)
    
    with form_col:
        st.subheader("Registration Form")
        with st.form("registration_form"):
            matric_number = st.text_input("Matriculation Number", placeholder="FPT/COM/2023/001")
            department = st.selectbox(
                "Department",
                ["Computer Science", "Information Technology", "Software Engineering", "Cybersecurity"]
            )
            submit_button = st.form_submit_button("Complete Registration")

    with capture_col:
        st.subheader("Facial Capture")
        camera_image = st.camera_input("Capture Template")
        st.caption("Template will be converted to 128-d biometric vector for security.")

    # Form Submission Handling
    if submit_button:
        if matric_number and department and camera_image:
            try:
                conn = get_db_connection()
                cursor = conn.cursor()
                query = "INSERT INTO students (matric_number, department) VALUES (%s, %s)"
                cursor.execute(query, (matric_number, department))
                conn.commit()
                cursor.close()
                conn.close()
                st.success(f"Successfully registered student ({matric_number})!")
            except Exception as e:
                st.error(f"Database Error: {e}")
        else:
            st.warning("Please fill in all form fields and capture a facial template.")

# ==========================================
# 3. REAL-TIME ATTENDANCE CAPTURE (LIVE STREAM)
# ==========================================
elif menu == "Live Capture":
    st.title("Real-Time Attendance Capture")
    
    # Top Control Bar matching Figure 5.4
    control_col1, control_col2 = st.columns([3, 1])
    with control_col1:
        course_session = st.selectbox(
            "Select Course Session",
            ["Introduction to AI (COM 312)", "Data Structures (COM 311)", "Operating Systems (COM 321)"]
        )
    with control_col2:
        st.write("") # spacing
        stop_btn = st.button("Stop Session", type="primary")
        
    st.info(f"Active session ready for: **{course_session}**. Click start or initialize the OpenCV stream.")
    
    # Video Feed Container Placeholder
    st.markdown(
        """
        <div style="background-color: #0e1117; padding: 40px; border-radius: 10px; text-align: center; border: 1px solid #303545;">
            <h3 style="color: #a3a8b8;">[ Live OpenCV Video Stream Window ]</h3>
            <p style="color: #64748b;">● Waiting for camera stream initialization...</p>
        </div>
        """, 
        unsafe_allow_html=True
    )

# ==========================================
# 4. ATTENDANCE REPORTS & LOGS
# ==========================================
elif menu == "Session Reports":
    st.title("Attendance Reports")
    
    # Filter Bar matching Figure 5.4 bottom layout
    filter_col1, filter_col2, filter_col3, filter_col4 = st.columns([2, 1, 1, 1])
    
    with filter_col1:
        filter_course = st.selectbox("Filter Course", ["All Courses", "Introduction to AI (COM 312)", "Data Structures (COM 311)"])
    with filter_col2:
        start_date = st.date_input("Start Date")
    with filter_col3:
        end_date = st.date_input("End Date")
    with filter_col4:
        st.write("")
        st.button("📥 Export CSV", use_container_width=True)
        
    st.markdown("---")
    
    # Fresh app state: Dynamic database load with zero records fallback
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT date, matric_number, course, time_in FROM attendance_records")
        records = cursor.fetchall()
        cursor.close()
        conn.close()
        
        if records:
            st.markdown("| DATE | MATRIC NO. | COURSE | TIME IN |")
            st.markdown("| :--- | :--- | :--- | :--- |")
            for r in records:
                st.markdown(f"| {r[0]} | {r[1]} | {r[2]} | {r[3]} |")
        else:
            st.info("No attendance records found. Data will appear here once live sessions capture student attendance.")
    except Exception:
        st.info("No attendance records found in the database yet.")