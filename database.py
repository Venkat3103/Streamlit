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
        SELECT department as department, product_name as product_name, price as Price
        FROM product.product_catalogue
    """
    product_catalogue = pd.read_sql(query, conn)
    product_catalogue['Quantity'] = 0
    product_catalogue['Select'] = False
    return product_catalogue

def fetch_order_details():
    #implement
    pass