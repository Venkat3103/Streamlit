import snowflake.connector
import config
import pandas as pd

# Snowflake connection parameters
snowflake_params = {
    'account': config.new_account,
    'user': config.new_user,
    'password': config.new_password,
    'warehouse': config.warehouse,
    'database': config.database,
    'schema': "orders",
    'role': config.role
}

# CSV file path
csv_file_path = '~/Downloads/order_items.csv'
#csv_file_path = '~/Downloads/order_details (6).csv'
# Read CSV into a Pandas DataFrame
df = pd.read_csv(csv_file_path)

# Connect to Snowflake
conn = snowflake.connector.connect(**snowflake_params)

# Create a cursor
cursor = conn.cursor()

# Insert data into Snowflake table using SQL in batches
table_name = 'order_items'
#table_name = 'order_details'
batch_size = 1000 

for i in range(0, len(df), batch_size):
    batch_df = df.iloc[i:i + batch_size]
    
    columns = ', '.join(batch_df.columns)
    print(columns)
    placeholders = ', '.join(['%s' for _ in range(len(batch_df.columns))])
    print(placeholders)
    insert_query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"

    # Convert DataFrame to a list of tuples for insertion
    data_to_insert = [tuple(row) for row in batch_df.values]

    # Execute the SQL query
    cursor.executemany(insert_query, data_to_insert)

# Commit the transaction
conn.commit()

# Close the connection
conn.close()
