# main.py

import streamlit as st
from forms import login_form, register_form
from order import order_page
from checkout import checkout_page
from database import get_database_connection
from shopper_order import modify_order
from shopper_insights import insights
from consumer_home import consumer_home
def select_user_class():
    user_class = st.radio("Select User Class", ["Consumer", "Shopper"], index=0)
    return user_class.lower() 

def main(conn):
    if "user_data" not in st.session_state:
        st.session_state.user_data = {}
    if "page" not in st.session_state:
        st.session_state["page"] = "home"
    # Select the user class
    if not st.session_state.user_data or st.session_state.page=="home":
        with st.container():
            st.title("Welcome to Grocery Shopping")
            form_option = st.selectbox("Select Action", ["Login", "Register"])
            user_class = select_user_class()
            st.session_state.user_data['user_class'] = user_class
            if form_option == "Login":
                login_form(conn,user_class)
                print(st.session_state)
            elif form_option == "Register":
                register_form(conn,user_class)

    elif st.session_state.user_data['user_class'] == "consumer": 
        if st.sidebar.button("Logout"):
            # Clear session state variables
            st.session_state.clear()
            # Redirect to the home page
            st.session_state.user_data = {}
            st.session_state.page = "home"
            st.rerun()
        if st.session_state.page == "consumer_home":
            consumer_home(conn)
        if st.session_state.page == "order":
            order_page(conn)
        elif st.session_state.page == "checkout":
            checkout_page(st.session_state.df[(st.session_state.df['Select'])&(st.session_state.df['Quantity']!=0)].drop('Select', axis=1), st.session_state.user_data['username'])
    elif st.session_state.user_data['user_class'] == "shopper":
        if st.sidebar.button("Logout"):
            # Clear session state variables
            st.session_state.clear()
            # Redirect to the home page
            st.session_state.user_data = {}
            st.session_state.page = "home"
            st.rerun()
        selected_page = st.sidebar.radio("Select Page", ["Shopper Dashboard", "Insights"])
        if selected_page == "Shopper Dashboard":
            modify_order(conn,st.session_state.user_data['username'])
        elif selected_page == "Insights":
            insights()

if __name__ == "__main__":
    conn = get_database_connection()
    main(conn)