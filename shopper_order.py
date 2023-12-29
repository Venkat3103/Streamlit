import streamlit as st
import config
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from database import get_all_shopper_orders, get_user_details, get_consumer_email,fetch_order_items

# Function to send email
def send_email(subject, body, to_email, attachment_path=None):
    st.write(subject, body,to_email)
    # Email configuration
    from_email = config.from_email
    email_password = config.email_password
    smtp_server = config.smtp_server
    smtp_port = config.smtp_port

    # Create message
    message = MIMEMultipart()
    message['From'] = from_email
    message['To'] = to_email
    message['Subject'] = subject

    # Attach body text
    message.attach(MIMEText(body, 'plain'))

    # Attach file if provided
    if attachment_path:
        with open(attachment_path, "rb") as attachment:
            part = MIMEApplication(attachment.read(), Name="edited_data.csv")
        part['Content-Disposition'] = f'attachment; filename="edited_data.csv"'
        message.attach(part)

    # Connect to SMTP server
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(from_email, email_password)
        server.sendmail(from_email, to_email, message.as_string())


def modify_order(conn,username):
    st.title("Welcome "+username)
    all_shopper_orders = get_all_shopper_orders(conn,username)
    selected_order_id = st.selectbox("Select Order",options = all_shopper_orders.ORDER_ID.to_list())
    df = fetch_order_items(conn,selected_order_id)
    #user this to get sender email. Currently commented because password setup required for gmail. Hence using gmail credentials from config file
    #shopper_email = get_user_details(conn,username).iloc[0]
    to_email = get_consumer_email(conn,selected_order_id).EMAIL.iloc[0]
    # Display editable DataFrame
    for index, row in df.iterrows():
        print(index)
        with st.form(f"Update Form for Row {index}"):
            # Create two columns for side-by-side display
            col1, col2, col3, col4 = st.columns(4)

            # Display editable fields for the specified columns
            col1.text_input("Product", value=str(row['PRODUCT_NAME']), key=f"product_name_{index}", disabled=True)
            col2.text_input("Department", value=row['DEPARTMENT'], key=f"DEPARTMENT{index}", disabled=True)
            updated_quantity = col3.text_input("QUANTITY", value=row['QUANTITY'], key=f"quantity_{index}")
            updated_price = col4.number_input("PRICE", value=row['UNIT_PRICE'], key=f"price_{index}")

            # Update the original DataFrame with the edited values
            if st.form_submit_button("Update"):
                if updated_price==row['UNIT_PRICE'] and updated_quantity==row['QUANTITY']:
                    st.error("No changes in values were observed")
                else:
                    # Perform action
                    df.loc[index, 'QUANTITY'] = updated_quantity
                    df.loc[index, 'UNIT_PRICE'] = updated_price
                    subject = "Order Modified"
                    body = "Hello,\n\nThe following item(s) has been modified in your order:\n\n"
                    old_record =  f"Your Order: Product: {row['PRODUCT_NAME']}, Department: {row['DEPARTMENT']}, Quantity: {row['QUANTITY']}, Price: {row['UNIT_PRICE']}\n"
                    email_body = f"\n\nUpdated Details: Product: {row['PRODUCT_NAME']}, Department: {row['DEPARTMENT']}, Quantity: {updated_quantity}, Price: {updated_price}"
                    #Query to update database
                    send_email(subject, body + old_record + email_body, to_email)
                    # Add your action here (e.g., execute SQL query)

    # Show the final updated DataFrame
    st.write("Updated Order Data:")
    st.dataframe(df,use_container_width=True,hide_index=True)
