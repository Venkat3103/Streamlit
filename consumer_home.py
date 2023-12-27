import streamlit as st
import pandas as pd
from database import get_database_connection, fetch_order_items, fetch_order_details, get_user_details


def fetch_order_items(conn, order_id):
    items_query = f"""
        SELECT pc.department, pc.product_name, oi.quantity, oi.unit_price
        FROM orders.order_items oi JOIN product.product_catalogue pc
        ON oi.product_id = pc.product_id
        WHERE oi.order_id = {order_id}
    """
    order_items = pd.read_sql(items_query, conn)
    return order_items

def fetch_order_details(conn, consumer_id):
    query = f"""
        SELECT *
        FROM orders.order_details
        WHERE consumer_id = {consumer_id}
    """
    order_details = pd.read_sql(query, conn)
    return order_details

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
    st.write("Welcome", st.session_state.user_data['username'])
    conn = get_database_connection()
    user_details = get_user_details(conn, st.session_state.user_data['username'])
    user_id = user_details.USER_ID.iloc[0]
    df = fetch_order_details(conn, user_id)
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
    if st.button(f"Start New Order"):
        st.session_state.page = "order"
        st.info("Redirecting to Order page")
        st.rerun()
