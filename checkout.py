import streamlit as st
import pandas as pd
from datetime import datetime
import numpy as np
from database import get_user_details


def get_user_ids(username,conn):
    cid = get_user_details(conn,username)
    shopper_id_query = """
                    SELECT USER_ID from user.user_data where USER_CLASS like 'shopper'
                    """
    sid = pd.read_sql(shopper_id_query,conn)
    st.write(cid)
    st.write(sid)
    return cid.USER_ID.loc[0],np.random.choice(sid.USER_ID.to_list())


def fetch_order_details(conn, consumer_id):
    query = f"""
        SELECT *
        FROM orders.order_details
        WHERE consumer_id = {consumer_id}
    """
    order_details = pd.read_sql(query, conn)
    return order_details

def checkout_page(order_details, username,conn):
    current_datetime = datetime.now()
    # Extract date and time components
    order_date = current_datetime.date()
    order_time = current_datetime.strftime('%H:%M:%S')

    title_col, _,goback_col = st.columns([4,2,1.5])
    with title_col:
        st.title("Checkout Page")

    # Back to order button
    with goback_col:
        st.write("    ")
        st.write("    ")
        if st.button("Back to Order"):
            pass
            #st.session_state.page = "order"
            #st.rerun()

    with st.form("delivery_form"):
        st.subheader("Delivery Details")
        delivery_address = st.text_input("Delivery Address:")
        delivery_date = st.date_input("Delivery Date:")
        delivery_time = st.time_input("Delivery Time:")

        st.subheader("Order Summary")
        st.dataframe(order_details, use_container_width=True, hide_index=True)

        # Calculate and display order total
        order_amount = (order_details['quantity'] * order_details['price']).sum()

        # Create three columns for Order Amount, Tip, and Total Amount
        col1, col2, col3 = st.columns([1, 1, 1])

        # Column 1: Order Amount
        with col1:
            st.write("Order Amount:")
            st.write(f"${order_amount:.2f}")

        # Column 2: Tip input
        with col2:
            tip = st.number_input(label = "Enter Tip", value=0.0, step=0.5)
            

        # Column 3: Total Amount
        with col3:
           st.write("Click to Place your Order")
           form_submit_button = st.form_submit_button(label="Place Order")

        # Form submit button
        

        # Show the review section only if the form is submitted and all fields are filled
        if form_submit_button:
            if delivery_address and delivery_date and delivery_time:
                # Write to Snowflake table
                # connection = create_snowflake_connection()
                consumer_id, shopper_id = get_user_ids(username,conn)
                total_amount = order_amount + tip

                st.write(order_amount,consumer_id,shopper_id,order_date, order_time, delivery_date , delivery_time,delivery_address,tip,total_amount)
                #st.write(get_product_id(order_details,conn))
                #create_order_query = f"""
                #INSERT INTO order_details (total_amount,consumer_id,shopper_id,order_date, order_time, delivery_date, delivery_time, delivery_address)
                #VALUES ('{order_amount}','{consumer_id}','{shopper_id}','{order_date}', '{order_time}','{delivery_date}', '{delivery_time}','{delivery_address}','{tip}','{total_amount}')
                #"""
                # execute_query(connection, create_order_query)
                # connection.close()

                st.success("Order placed successfully! Thank you for your purchase.")
            else:
                st.warning("Please fill in all the delivery details before placing the order.")

