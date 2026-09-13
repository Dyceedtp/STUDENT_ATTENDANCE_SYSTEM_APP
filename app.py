import streamlit as st
import mysql.connector

# Connect to your Aiven MySQL database
def get_db_connection():
    return mysql.connector.connect(
        host="your_aiven_host",
        user="your_db_user",
        password="your_db_password",
        database="your_database_name",
        port=3306
    )

st.title("Student Biometric Enrollment")

# Create the registration form layout matching your project document
with st.form("registration_form"):
    st.subheader("Registration Form")
    
    full_name = st.text_input("Full Name")
    matric_number = st.text_input("Matriculation Number")
    
    # Department dropdown (you can customize these options to fit your school)
    department = st.selectbox(
        "Department",
        ["Computer Science", "Information Technology", "Software Engineering", "Cybersecurity"]
    )
    
    # Placeholder for the camera capture section
    st.info("Facial Capture will use your webcam to generate the biometric template.")
    camera_image = st.camera_input("Capture Student Face Template")
    
    submit_button = st.form_submit_button("Complete Registration")

    if submit_button:
        if full_name and matric_number and camera_image:
            try:
                conn = get_db_connection()
                cursor = conn.cursor()
                
                # SQL query to insert student details into your database
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
            st.warning("Please fill in all fields and capture a facial image before submitting.")