import streamlit as st
from security import check_password

def get_or_create_user_data():
    if 'user_data' not in st.session_state:
        st.session_state.user_data = {}
    return st.session_state.user_data

def insert_registration_data(conn,username, email, phone_number, hashed_password, user_class):
    with conn.cursor() as cursor:
            cursor.execute(f"SELECT * FROM user_data WHERE username = '{username}' OR email = '{email}' OR phone_number = '{phone_number}'")
            existing_user = cursor.fetchone()

            if existing_user:
                st.error("Username, email, or phone number already exists. Please choose different credentials.")
                return False

            cursor.execute("""
                INSERT INTO user_data (username, email, phone_number, hashed_password, user_class)
                VALUES (%s, %s, %s, %s, %s)
            """, (username, email, phone_number, hashed_password, user_class))
            return True

def validate_login(conn,username, password, user_class):
    with conn.cursor() as cursor:
            cursor.execute(f"SELECT * FROM user_data WHERE username = '{username}' AND user_class = '{user_class}'")
            user_data = cursor.fetchone()

            if user_data:
                stored_hashed_password = bytes(user_data[4])

                if check_password(password, stored_hashed_password):
                    return user_data
