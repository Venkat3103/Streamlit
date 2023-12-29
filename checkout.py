import streamlit as st
import pandas as pd
from datetime import datetime
import numpy as np
from database import get_user_details, insert_new_order_details, get_user_ids

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
            st.session_state.page = "order"
            st.rerun()

    with st.form("delivery_form"):
        st.subheader("Delivery Details")
        delivery_address = st.text_input("Delivery Address:")
        delivery_date = st.date_input("Delivery Date:")
        delivery_time = st.time_input("Delivery Time:")

        st.subheader("Order Summary")
        st.dataframe(order_details, use_container_width=True, hide_index=True, column_config={"PRODUCT_ID":None})

        # Calculate and display order total
        order_amount = (order_details['Quantity'] * order_details['PRICE']).sum()

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
                consumer_id, shopper_id = get_user_ids(username,conn)
                total_amount = order_amount + tip
                order_items_df = order_details.copy()[['PRODUCT_ID','Quantity','PRICE']]
                order_items_df = order_items_df.rename(columns={"PRICE":"UNIT_PRICE"})
                #pd_writer.write_pandas(conn, order_items_df, "order_items", schema="orders", if_exists='append', index=False)
                insert_order_details_query = f"""
                INSERT INTO orders.order_details (order_amount,consumer_id,shopper_id,order_date, order_time, delivery_date, delivery_time, delivery_address, tip, total_amount)
                VALUES ('{order_amount}','{consumer_id}','{shopper_id}','{order_date}', '{order_time}','{delivery_date}', '{delivery_time}','{delivery_address}','{tip}','{total_amount}')
                """
                cursor = conn.cursor()
                cursor.execute(insert_order_details_query)

                order_number_query = f"""SELECT ORDER_ID from orders.order_details ORDER BY ORDER_ID DESC LIMIT 1"""
                last_order_id = pd.read_sql(order_number_query,conn).ORDER_ID.iloc[0]
                order_items_df['ORDER_ID'] = last_order_id
                insert_new_order_details(conn,order_items_df)

                st.write("Your order number is: ",str(last_order_id))
                st.success("Order placed successfully! Thank you for your purchase")
                keys_to_keep = ['page', 'user_data']

                # Clear everything in session_state except keys_to_keep
                for key in list(st.session_state.keys()):
                    if key not in keys_to_keep:
                        del st.session_state[key]
                st.session_state.page = "consumer_home"
                st.rerun()
            else:
                st.warning("Please fill in all the delivery details before placing the order.")

