import config
import pandas as pd
import numpy as np
import streamlit as st
import snowflake.connector

def get_database_connection():
    return snowflake.connector.connect(
        account = config.account,
        user = config.user,
        password = config.password,
        warehouse = config.warehouse,
        role = config.role,
        database = config.database,
        schema = config.schema
    )

# Function to fetch all unique departments from the database
def get_all_departments(conn):
    with conn.cursor() as cursor:
        cursor.execute("SELECT DISTINCT department FROM product.product_catalogue")
        departments = [row[0] for row in cursor.fetchall()]
        return departments

def get_initial_df(conn):
    query = f"""
        SELECT product_id as product_id, department as department, product_name as product_name, price as Price
        FROM product.product_catalogue
    """
    product_catalogue = pd.read_sql(query, conn)
    product_catalogue['Quantity'] = 0
    product_catalogue['Select'] = False
    return product_catalogue

def fetch_order_items(conn, order_id):
    items_query = f"""
        SELECT pc.product_id, pc.department, pc.product_name, oi.quantity, oi.unit_price
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

def get_user_details(conn, username):
    query = f"""
        SELECT *
        FROM user.user_data
        WHERE username = '{username}'
    """
    user_details = pd.read_sql(query, conn)
    return user_details

def get_all_shopper_orders(conn,username):
    query = f"""
        SELECT *
        FROM orders.order_details od JOIN user.user_data ud
        ON od.shopper_id = ud.user_id
        WHERE ud.username = '{username}'
    """
    shopper_orders = pd.read_sql(query, conn)
    return shopper_orders

def get_consumer_email(conn, order_id):
    query = f"""
        WITH consumer_details as (SELECT consumer_id FROM orders.order_details where order_id = {order_id} )
        SELECT ud.email 
        FROM user.user_data ud 
        JOIN consumer_details cd
        on ud.user_id = cd.consumer_id
    """
    return pd.read_sql(query,conn)

def update_order_item(conn, item_df, order_id):
    print(item_df.dtypes)
    #item_df['QUANTITY'] = item_df['QUANTITY'].astype(int)
    print(item_df.dtypes)
    print("QUERY 1")
    query1 = f"""
    UPDATE orders.order_items
    SET quantity = {item_df['QUANTITY']}, unit_price = {item_df['UNIT_PRICE']}
    WHERE ORDER_ID = {order_id}
    AND product_id = {item_df['PRODUCT_ID']}
    """
    print("QUERY 2")
    query2 = f"""
    UPDATE orders.order_details od
    SET order_amount = (
        SELECT COALESCE(SUM(quantity * unit_price), 0) AS new_order_amount
        FROM orders.order_items
        WHERE order_id = {order_id}
    )
    WHERE od.ORDER_ID = {order_id}
    """

    try:
        cursor = conn.cursor()
        
        # Begin the transaction
        cursor.execute("BEGIN TRANSACTION")

        # Execute the first query
        cursor.execute(query1)

        # Execute the second query
        cursor.execute(query2)

        # Commit the transaction
        conn.commit()

        cursor.close()
        print("Executed")
        return True  # Return True to indicate success

    except Exception as e:
        # Handle the exception (e.g., print an error message)
        print(f"Error executing query: {e}")

        # Rollback the transaction
        cursor.execute("ROLLBACK")

        return False  # Return False to indicate failure

def insert_new_order_items(conn,df):
    table_name = 'order_items'
    batch_size = 1000 
    cursor = conn.cursor()
    for i in range(0, len(df), batch_size):
        batch_df = df.iloc[i:i + batch_size]
        
        columns = ', '.join(batch_df.columns)
        print(columns)
        placeholders = ', '.join(['%s' for _ in range(len(batch_df.columns))])
        print(placeholders)
        insert_query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"

        # Convert DataFrame to a list of tuples for insertion
        data_to_insert = [tuple(row) for row in batch_df.values]
        st.write(data_to_insert)
        # Execute the SQL query
        cursor.executemany(insert_query, data_to_insert)

# Commit the transaction
    conn.commit()

def insert_new_order_details(conn,df):
    table_name = 'orders.order_items'
    batch_size = 1000 
    cursor = conn.cursor()
    for i in range(0, len(df), batch_size):
        batch_df = df.iloc[i:i + batch_size]
        columns = ', '.join(batch_df.columns)
        print(columns)
        placeholders = ', '.join(['%s' for _ in range(len(batch_df.columns))])
        print(placeholders)
        insert_query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
        st.write(insert_query)
        # Convert DataFrame to a list of tuples for insertion
        data_to_insert = [tuple(row) for row in batch_df.values]

        # Execute the SQL query
        cursor.executemany(insert_query, data_to_insert)

# Commit the transaction
    conn.commit()

def get_user_ids(username,conn):
    cid = get_user_details(conn,username)
    shopper_id_query = """
                    SELECT USER_ID from user.user_data where USER_CLASS like 'shopper'
                    """
    sid = pd.read_sql(shopper_id_query,conn)
    return cid.USER_ID.loc[0],np.random.choice(sid.USER_ID.to_list())

