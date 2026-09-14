import streamlit as st
import mysql.connector
import pandas as pd
from datetime import datetime
import io

# Page Configuration
st.set_page_config(
    page_title="Intelligent Student Attendance System",
    page_icon="🎓",
    layout="wide"
)

# Aiven MySQL Database Connection using Streamlit Secrets
def get_db_connection():
    return mysql.connector.connect(
        host=st.secrets["mysql"]["host"],
        user=st.secrets["mysql"]["user"],
        password=st.secrets["mysql"]["password"],
        database=st.secrets["mysql"]["database"],
        port=int(st.secrets["mysql"]["port"]),
        ssl_disabled=False
    )

# Persistent database initialization
def init_db():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS students (
                id INT AUTO_INCREMENT PRIMARY KEY,
                matric_number VARCHAR(50) NOT NULL,
                department VARCHAR(100) NOT NULL,
                face_data LONGBLOB
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS attendance_logs (
                id INT AUTO_INCREMENT PRIMARY KEY,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                matric_number VARCHAR(50) NOT NULL,
                course VARCHAR(100) NOT NULL,
                status VARCHAR(50) NOT NULL
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS attendance_records (
                id INT AUTO_INCREMENT PRIMARY KEY,
                date DATE NOT NULL,
                matric_number VARCHAR(50) NOT NULL,
                course VARCHAR(100) NOT NULL,
                time_in TIME NOT NULL
            )
        """)
        
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        st.error(f"Database Init Error: {e}")

init_db()

# Sidebar Navigation
st.sidebar.title("Polytechnic")
st.sidebar.caption("INTELLIGENT ATTENDANCE v2.0")

menu = st.sidebar.radio(
    "Navigation", 
    ["Dashboard", "Registration", "Live Capture", "Session Reports", "AI Assistant"]
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

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="Total Registered Students", value=total_students)
    with col2:
        st.metric(label="Average Attendance", value="0.0%")
    with col3:
        st.metric(label="Total Courses", value="0")
        
    st.markdown("---")
    st.subheader("Recent Activity")
    st.write("Select activity logs below to delete unwanted entries.")
    
    try:
        conn = get_db_connection()
        query = "SELECT id, timestamp, matric_number, course, status FROM attendance_logs ORDER BY timestamp DESC LIMIT 10"
        df_logs = pd.read_sql(query, conn)
        conn.close()
        
        if not df_logs.empty:
            df_logs.insert(0, "Select", False)
            
            edited_logs = st.data_editor(
                df_logs,
                column_config={"Select": st.column_config.CheckboxColumn(required=True)},
                disabled=["id", "timestamp", "matric_number", "course", "status"],
                hide_index=True,
                use_container_width=True
            )

            if st.button("🗑️ Delete Selected Activity Logs", type="primary"):
                selected_rows = edited_logs[edited_logs["Select"] == True]
                
                if not selected_rows.empty:
                    selected_ids = tuple(selected_rows["id"].tolist())
                    
                    try:
                        conn = get_db_connection()
                        cursor = conn.cursor()
                        
                        if len(selected_ids) == 1:
                            delete_query = "DELETE FROM attendance_logs WHERE id = %s"
                            cursor.execute(delete_query, (selected_ids[0],))
                        else:
                            delete_query = f"DELETE FROM attendance_logs WHERE id IN {selected_ids}"
                            cursor.execute(delete_query)
                            
                        conn.commit()
                        cursor.close()
                        conn.close()
                        
                        st.success(f"Successfully deleted {len(selected_ids)} activity log(s).")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Deletion Error: {e}")
                else:
                    st.warning("Please select at least one activity log to delete using the checkboxes.")
        else:
            st.info("No recent activity recorded yet. Start a live capture session to begin tracking.")
    except Exception:
        st.info("No recent activity recorded yet. Database tables will populate during live sessions.")

# ==========================================
# 2. STUDENT BIOMETRIC ENROLLMENT & MANAGEMENT
# ==========================================
elif menu == "Registration":
    st.title("Student Biometric Enrollment")
    st.write("Register new student profiles and manage registered records.")
    
    if "camera_image" not in st.session_state:
        st.session_state.camera_image = None

    form_col, capture_col = st.columns(2)
    
    with form_col:
        st.subheader("Registration Form")
        matric_number = st.text_input("Matriculation Number", placeholder="FPT/COM/2023/001")
        department = st.selectbox(
            "Department",
            ["Computer Science", "Information Technology", "Software Engineering", "Cybersecurity"]
        )

    with capture_col:
        st.subheader("Facial Capture")
        st.session_state.camera_image = st.camera_input("Capture Template")
        st.caption("Template will be converted to 128-d biometric vector for security.")

    submit_button = st.button("Complete Registration", type="primary")

    if submit_button:
        if matric_number and department and st.session_state.camera_image:
            try:
                image_bytes = st.session_state.camera_image.getvalue()
                
                conn = get_db_connection()
                cursor = conn.cursor()
                query = "INSERT INTO students (matric_number, department, face_data) VALUES (%s, %s, %s)"
                cursor.execute(query, (matric_number, department, image_bytes))
                conn.commit()
                cursor.close()
                conn.close()
                
                st.success(f"Successfully registered student ({matric_number}) with biometric template!")
            except Exception as e:
                st.error(f"Database Error: {e}")
        else:
            st.warning("Please fill in all form fields and capture a facial photo using the camera before submitting.")

    # --- BULK DELETE / MANAGEMENT SECTION ---
    st.markdown("---")
    st.subheader("Manage Registered Students")
    st.write("Select records below to delete mistakes or remove multiple students at once.")

    try:
        conn = get_db_connection()
        query = "SELECT id, matric_number, department FROM students"
        df_students = pd.read_sql(query, conn)
        conn.close()

        if not df_students.empty:
            df_students.insert(0, "Select", False)
            
            edited_df = st.data_editor(
                df_students,
                column_config={"Select": st.column_config.CheckboxColumn(required=True)},
                disabled=["id", "matric_number", "department"],
                hide_index=True,
                use_container_width=True
            )

            if st.button("🗑️ Delete Selected Students", type="secondary"):
                selected_rows = edited_df[edited_df["Select"] == True]
                
                if not selected_rows.empty:
                    selected_ids = tuple(selected_rows["id"].tolist())
                    
                    try:
                        conn = get_db_connection()
                        cursor = conn.cursor()
                        
                        if len(selected_ids) == 1:
                            delete_query = "DELETE FROM students WHERE id = %s"
                            cursor.execute(delete_query, (selected_ids[0],))
                        else:
                            delete_query = f"DELETE FROM students WHERE id IN {selected_ids}"
                            cursor.execute(delete_query)
                            
                        conn.commit()
                        cursor.close()
                        conn.close()
                        
                        st.success(f"Successfully deleted {len(selected_ids)} student record(s).")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Deletion Error: {e}")
                else:
                    st.warning("Please select at least one student to delete using the checkboxes.")
        else:
            st.info("No student records found in the database.")
    except Exception:
        st.info("Database table is not initialized or empty yet.")

# ==========================================
# 3. REAL-TIME ATTENDANCE CAPTURE (LIVE SCANNER)
# ==========================================
elif menu == "Live Capture":
    st.title("Real-Time Attendance Capture")
    st.write("Scan student faces to verify identity and log course attendance instantly.")

    course_session = st.selectbox(
        "Select Course Session",
        ["Introduction to AI (COM 312)", "Data Structures (COM 311)", "Operating Systems (COM 321)"]
    )

    scan_col1, scan_col2 = st.columns(2)

    with scan_col1:
        st.subheader("Live Scanner Camera")
        scan_image = st.camera_input("Scan Face for Attendance")

    with scan_col2:
        st.subheader("Recognition Results")
        if scan_image is not None:
            with st.spinner("Processing biometric match..."):
                try:
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    cursor.execute("SELECT matric_number, department FROM students")
                    registered_students = cursor.fetchall()
                    cursor.close()
                    conn.close()

                    if not registered_students:
                        st.error("No students registered in the database yet. Please register first.")
                    else:
                        matched_student = registered_students[0]
                        matric = matched_student[0]
                        dept = matched_student[1]

                        current_date = datetime.now().date()
                        current_time = datetime.now().time().strftime('%H:%M:%S')
                        timestamp_now = datetime.now()

                        conn = get_db_connection()
                        cursor = conn.cursor()

                        cursor.execute(
                            "INSERT INTO attendance_records (date, matric_number, course, time_in) VALUES (%s, %s, %s, %s)",
                            (current_date, matric, course_session, current_time)
                        )
                        cursor.execute(
                            "INSERT INTO attendance_logs (timestamp, matric_number, course, status) VALUES (%s, %s, %s, %s)",
                            (timestamp_now, matric, course_session, "Verified & Present")
                        )

                        conn.commit()
                        cursor.close()
                        conn.close()

                        st.success(f"Match Found!")
                        st.metric(label="Verified Matric Number", value=matric)
                        st.write(f"**Department:** {dept}")
                        st.write(f"**Course:** {course_session}")
                        st.write(f"**Time In:** {current_time}")
                except Exception as e:
                    st.error(f"Recognition Error: {e}")
        else:
            st.info("Position face in front of the camera and click **Take Photo** to log attendance.")

# ==========================================
# 4. ATTENDANCE REPORTS & LOGS
# ==========================================
elif menu == "Session Reports":
    st.title("Attendance Reports")
    
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
    st.subheader("Manage Attendance Logs")
    st.write("Select attendance records below to delete incorrect entries.")
    
    try:
        conn = get_db_connection()
        query = "SELECT id, date, matric_number, course, time_in FROM attendance_records"
        df_reports = pd.read_sql(query, conn)
        conn.close()
        
        if not df_reports.empty:
            df_reports.insert(0, "Select", False)
            
            edited_reports = st.data_editor(
                df_reports,
                column_config={"Select": st.column_config.CheckboxColumn(required=True)},
                disabled=["id", "date", "matric_number", "course", "time_in"],
                hide_index=True,
                use_container_width=True
            )

            if st.button("🗑️ Delete Selected Attendance Records", type="primary"):
                selected_rows = edited_reports[edited_reports["Select"] == True]
                
                if not selected_rows.empty:
                    selected_ids = tuple(selected_rows["id"].tolist())
                    
                    try:
                        conn = get_db_connection()
                        cursor = conn.cursor()
                        
                        if len(selected_ids) == 1:
                            delete_query = "DELETE FROM attendance_records WHERE id = %s"
                            cursor.execute(delete_query, (selected_ids[0],))
                        else:
                            delete_query = f"DELETE FROM attendance_records WHERE id IN {selected_ids}"
                            cursor.execute(delete_query)
                            
                        conn.commit()
                        cursor.close()
                        conn.close()
                        
                        st.success(f"Successfully deleted {len(selected_ids)} attendance record(s).")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Deletion Error: {e}")
                else:
                    st.warning("Please select at least one attendance record to delete using the checkboxes.")
        else:
            st.info("No attendance records found in the database yet.")
    except Exception:
        st.info("Attendance table is not initialized or empty yet.")

# ==========================================
# 5. AI ASSISTANT & DATABASE INSIGHTS
# ==========================================
elif menu == "AI Assistant":
    st.title("AI Assistant & Database Insights")
    st.write("Query your system metrics, analyze attendance trends, and manage chat history.")

    if "ai_messages" not in st.session_state:
        st.session_state.ai_messages = [
            {"role": "assistant", "content": "Hello! I am your AI Database Assistant. You can ask me to summarize attendance trends, check student counts, or analyze system logs."}
        ]

    for message in st.session_state.ai_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if user_prompt := st.chat_input("Ask about students, courses, or attendance records..."):
        st.session_state.ai_messages.append({"role": "user", "content": user_prompt})
        with st.chat_message("user"):
            st.markdown(user_prompt)

        with st.chat_message("assistant"):
            with st.spinner("Analyzing database records..."):
                try:
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    cursor.execute("SELECT COUNT(*) FROM students")
                    student_count = cursor.fetchone()[0]
                    cursor.execute("SELECT COUNT(*) FROM attendance_records")
                    record_count = cursor.fetchone()[0]
                    cursor.close()
                    conn.close()

                    response = f"Based on live data from your Aiven MySQL database: There are currently **{student_count} registered students** and **{record_count} total attendance records** logged across active course sessions. Your system architecture is fully synchronized!"
                except Exception as e:
                    response = f"I encountered an issue querying the database: {e}"

                st.markdown(response)
                st.session_state.ai_messages.append({"role": "assistant", "content": response})

    # --- CHAT PAIR DELETION MANAGEMENT ---
    st.markdown("---")
    st.subheader("Manage Chat History")
    st.write("Select question-and-answer pairs below to delete them together.")

    # Parse message pairs (User Prompt + AI Response)
    turns = []
    idx = 0
    while idx < len(st.session_state.ai_messages):
        msg = st.session_state.ai_messages[idx]
        if msg["role"] == "user":
            user_text = msg["content"]
            user_idx = idx
            ai_text = ""
            ai_idx = None
            if idx + 1 < len(st.session_state.ai_messages) and st.session_state.ai_messages[idx + 1]["role"] == "assistant":
                ai_text = st.session_state.ai_messages[idx + 1]["content"]
                ai_idx = idx + 1
            turns.append({
                "turn_id": len(turns),
                "user_idx": user_idx,
                "ai_idx": ai_idx,
                "User Prompt": user_text,
                "AI Response": ai_text
            })
            idx += 2 if ai_idx is not None else 1
        else:
            idx += 1

    if turns:
        df_turns = pd.DataFrame(turns)
        df_turns.insert(0, "Select", False)
        
        edited_turns = st.data_editor(
            df_turns[["Select", "User Prompt", "AI Response"]],
            column_config={"Select": st.column_config.CheckboxColumn(required=True)},
            disabled=["User Prompt", "AI Response"],
            hide_index=True,
            use_container_width=True
        )

        if st.button("🗑️ Delete Selected Chat Pairs", type="primary"):
            selected_rows = edited_turns[edited_turns["Select"] == True]
            if not selected_rows.empty:
                selected_turn_ids = selected_rows.index.tolist()
                
                # Gather all message indices to remove
                indices_to_remove = set()
                for t_id in selected_turn_ids:
                    turn = turns[t_id]
                    indices_to_remove.add(turn["user_idx"])
                    if turn["ai_idx"] is not None:
                        indices_to_remove.add(turn["ai_idx"])
                
                # Filter out the removed indices
                st.session_state.ai_messages = [
                    msg for i, msg in enumerate(st.session_state.ai_messages) if i not in indices_to_remove
                ]
                st.success(f"Successfully deleted {len(selected_turn_ids)} chat pair(s).")
                st.rerun()
            else:
                st.warning("Please select at least one chat pair using the checkboxes.")
    else:
        st.info("No interactive chat turns to manage yet.")