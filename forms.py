import streamlit as st
from user_data import validate_login, insert_registration_data
from security import hash_password


def login_form(conn,user_class):
    st.header("User Login")
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        submitted = st.form_submit_button("Login")

        if submitted:
            user_data = validate_login(conn, username, password, user_class)

            if user_data:
                st.success(f"Logged in as {user_class}: {username}")
                
                # Store user details in session state
                st.session_state.user_data = {
                    "username": username,
                    "user_class": user_class
                }
                st.empty()
                if user_class.lower() == "consumer":
                    st.info("Login Successful...")
                    st.empty()
                    st.session_state["page"] = "consumer_home"
                    st.write(st.session_state)
                    st.rerun()
                elif user_class.lower() == "shopper":
                    st.info("Redirecting to Shopper Page")
                    st.empty()
                    st.session_state["page"] = "shopper_order"
                    st.rerun()
                    st.write(st.session_state)
                    # Add code to redirect to the shopper page
            else:
                st.error("Invalid username or password")

def register_form(conn,user_class):
    st.header("Register")

    with st.form("registration_form"):
        new_username = st.text_input("New Username")
        new_email = st.text_input("Email")
        new_phone_number = st.text_input("Phone Number")
        new_password = st.text_input("New Password", type="password")

        submitted = st.form_submit_button("Register")

        if submitted:
            if not all([new_username, new_email, new_phone_number, new_password]):
                st.error("Please fill in all fields.")
            else:
                hashed_password = hash_password(new_password)
                insert_registration_data(conn,new_username, new_email, new_phone_number, hashed_password, user_class.lower())
                st.success(f"Registered new {user_class.lower()}: {new_username}")
                st.info(f"Email: {new_email}")
                st.info(f"Phone Number: {new_phone_number}")
                st.info(f"User Class: {user_class}")
