import streamlit as st
import mysql.connector

try:
    # Attempt to establish connection using Streamlit secrets
    db = mysql.connector.connect(
        host=st.secrets["mysql"]["host"],
        port=int(st.secrets["mysql"]["port"]),
        user=st.secrets["mysql"]["user"],
        password=st.secrets["mysql"]["password"],
        database=st.secrets["mysql"]["database"]
    )
except Exception as e:
    # Display clear diagnostic information on the live page if it fails
    st.error("Database Connection Failed!")
    st.error(f"Host read: {st.secrets['mysql'].get('host', 'MISSING')}")
    st.error(f"Port read: {st.secrets['mysql'].get('port', 'MISSING')}")
    st.error(f"Detailed Error: {e}")
    raise e