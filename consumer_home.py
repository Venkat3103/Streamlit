import streamlit as st
import pandas as pd
from database import get_database_connection, fetch_order_items, fetch_order_details, get_user_details

def generate_receipt(order_details, order_items):
    # Replace this with your logic to generate the receipt content
    receipt_content = f"Order ID: {order_details['ORDER_ID']}\n"
    receipt_content += f"Order Date: {order_details['ORDER_DATE']} {order_details['ORDER_TIME']}\n"
    receipt_content += f"Delivery Date: {order_details['DELIVERY_DATE']} {order_details['DELIVERY_TIME']}\n"
    receipt_content += f"Delivery Address: {order_details['DELIVERY_ADDRESS']}\n"
    receipt_content += "\nOrder Items:\n"

    for _, item in order_items.iterrows():
        receipt_content += f"Department: {item['DEPARTMENT']}, Item: {item['PRODUCT_NAME']}, Quantity: {item['QUANTITY']}, Unit Price: ${item['UNIT_PRICE']:.2f}\n"

    receipt_content += f"\nTotal Amount: ${order_details['TOTAL_AMOUNT']:.2f}"
    return receipt_content

def consumer_home(conn):
    username =  st.session_state.user_data['username']
    st.title("Welcome "+username)
    user_details = get_user_details(conn, st.session_state.user_data['username'])
    user_id = user_details.USER_ID.iloc[0]
    df = fetch_order_details(conn, user_id)
    selected_order = st.selectbox(label = "Select your Order to view details",options = df.ORDER_ID.to_list())
    df = df[df['ORDER_ID']==selected_order]
    for _, order_row in df.iterrows():
        # Display order details
        with st.expander(f"Order ID: {order_row['ORDER_ID']}"):
            st.write(f"Order Date: {order_row['ORDER_DATE']} {order_row['ORDER_TIME']}")
            st.write(f"Delivery Date: {order_row['DELIVERY_DATE']} {order_row['DELIVERY_TIME']}")
            st.write(f"Delivery Address: {order_row['DELIVERY_ADDRESS']}")
            st.write("Order Items:")

            # Fetch order items for the current order_id
            items = fetch_order_items(conn, order_row['ORDER_ID'])
            st.dataframe(items,hide_index=True)
            data = generate_receipt(order_row, items)
            # Download button for the receipt
            
            # Generate and download the receipt
            st.download_button(
                label="Download Receipt",
                data=data,
                file_name=f"receipt_order_{order_row['ORDER_ID']}.txt",
                key=f"download_receipt_{order_row['ORDER_ID']}_button"
            )

        # Start a new order button
    if st.button(f"Start a New Order"):
        st.session_state.page = "order"
        st.info("Redirecting to Order page")
        st.rerun()
