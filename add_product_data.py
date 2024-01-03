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
    'schema': config.schema,
    'role': config.role
}

# CSV file path
csv_file_path = '~/Downloads/product_catalogue.csv'

# Read CSV into a Pandas DataFrame
df = pd.read_csv(csv_file_path)

# Connect to Snowflake
conn = snowflake.connector.connect(**snowflake_params)

# Create a cursor
cursor = conn.cursor()

# Insert data into Snowflake table using SQL in batches
table_name = 'PRODUCT.PRODUCT_CATALOGUE'
batch_size = 1000 

for i in range(0, len(df), batch_size):
    batch_df = df.iloc[i:i + batch_size]
    
    columns = ', '.join(batch_df.columns)
    placeholders = ', '.join(['%s' for _ in range(len(batch_df.columns))])
    insert_query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"

    # Convert DataFrame to a list of tuples for insertion
    data_to_insert = [tuple(row) for row in batch_df.values]

    # Execute the SQL query
    cursor.executemany(insert_query, data_to_insert)

# Commit the transaction
conn.commit()

# Close the connection
conn.close()
