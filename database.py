import config
import pandas as pd
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
