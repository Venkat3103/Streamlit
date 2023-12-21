#create a form to get all the details, near form submit, have a checkbox which says download receipt
import streamlit as st
from order import order_page
def checkout_page(order_details, username):
    print("entered")
    st.title("Checkout Page")

    st.header("Order Summary")
    st.write(f"Username: {username}")
    st.write(f"Products: {order_details['PRODUCT_NAME']}")
    st.write(f"Quantity: {order_details['Quantity']}")
    #st.write(f"Delivery Date: {order_details['delivery_date']}")
    
    #st.write(f"Delivery Time: {order_details['delivery_time']}")

    st.header("Delivery Details")
    address, zipcode, tip = delivery_details()

    if st.button("Submit Order"):
        st.session_state.page = "order"
        st.rerun()
        # Add necessary imports and replace placeholders with actual function calls

def delivery_details():
    address = st.text_input("Delivery Address")
    zipcode = st.text_input("Zipcode")
    tip = st.number_input("Tip for Shopper", min_value=0, step=1, value=0)

    return address, zipcode, tip
