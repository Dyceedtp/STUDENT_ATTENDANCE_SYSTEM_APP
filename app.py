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

# Sidebar Navigation matching your project documentation
st.sidebar.title("Polytechnic Portal")
menu = st.sidebar.selectbox("Navigation", ["Dashboard", "Registration", "Live Capture", "Session Reports"])

if menu == "Dashboard":
    st.title("Admin Dashboard")
    st.write("Welcome to the Intelligent Student Attendance System. Use the sidebar to navigate between student biometric enrollment and real-time attendance tracking.")

elif menu == "Registration":
    st.title("Student Biometric Enrollment")
    
    # Form layout matching Figure 5.2 of your project documentation
    with st.form("registration_form"):
        st.subheader("Registration Form")
        
        full_name = st.text_input("Full Name")
        matric_number = st.text_input("Matriculation Number")
        
        department = st.selectbox(
            "Department",
            ["Computer Science", "Information Technology", "Software Engineering", "Cybersecurity"]
        )
        
        st.info("Facial Capture will use your camera to generate the biometric template.")
        camera_image = st.camera_input("Capture Student Face Template")
        
        submit_button = st.form_submit_button("Complete Registration")

        if submit_button:
            if full_name and matric_number and camera_image:
                try:
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    
                    # Insert record into Aiven MySQL database
                    query = """
                        INSERT INTO students (full_name, matric_number, department) 
                        VALUES (%s, %s, %s)
                    """
                    cursor.execute(query, (full_name, matric_number, department))
                    conn.commit()
                    
                    cursor.close()
                    conn.close()
                    
                    st.success(f"Successfully registered {full_name} ({matric_number})!")
                except Exception as e:
                    st.error(f"Database Error: {e}")
            else:
                st.warning("Please fill in all required fields and capture a facial image.")

elif menu == "Live Capture":
    st.title("Real-Time Attendance Capture")
    st.info("The live OpenCV video feed and biometric face-matching stream will run here.")
    # Placeholder for starting live stream session
    if st.button("Start Attendance Session"):
        st.warning("OpenCV live stream integration is ready to be initialized.")

elif menu == "Session Reports":
    st.title("Attendance Session Reports")
    st.write("View logs, attendance history, and run natural language queries here.")