import streamlit as st
import config
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

#dummy order data
def get_data():
    product_catalogue = pd.read_csv("~/Downloads/product_catalogue.csv")
    product_catalogue['Quantity'] = 10
    return product_catalogue[['product_name','department','Quantity','Price']].head(5)

# Function to send email
def send_email(subject, body, to_email, attachment_path=None):
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

def modify_order():
    df = get_data()
    # Display editable DataFrame
    for index, row in df.iterrows():
        print(index)
        with st.form(f"Update Form for Row {index}"):
            # Create two columns for side-by-side display
            col1, col2, col3, col4 = st.columns(4)

            # Display editable fields for the specified columns
            col1.text_input("Product", value=str(row['product_name']), key=f"product_name_{index}", disabled=True)
            col2.text_input("Department", value=row['department'], key=f"department_{index}", disabled=True)
            updated_quantity = col3.text_input("Quantity", value=row['Quantity'], key=f"quantity_{index}")
            updated_price = col4.number_input("Price", value=row['Price'], key=f"price_{index}")

            # Update the original DataFrame with the edited values
            if st.form_submit_button("Update"):
                df.loc[index, 'Quantity'] = updated_quantity
                df.loc[index, 'Price'] = updated_price
                # Perform action
                subject = "Order Modified"
                body = "Hello,\n\nThe following item(s) has been modified in your order:\n\n"
                old_record =  f"Your Order: Product: {row['product_name']}, Department: {row['department']}, Quantity: {row['Quantity']}, Price: {row['Price']}\n"
                email_body = f"Updated Details: Product: {row['product_name']}, Department: {row['department']}, Quantity: {updated_quantity}, Price: {updated_price}"
                send_email(subject, body + old_record + email_body, to_email='n.venkat3103@gmail.com')
                # Add your action here (e.g., execute SQL query)

    # Show the final updated DataFrame
    st.write("Final Updated DataFrame:")
    st.write(df)
