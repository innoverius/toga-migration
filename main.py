import pyodbc

# Define the connection string
server = 'localhost'  # or the server name/IP
database = 'toga'
username = 'your_username'  # replace with your username
password = 'V_p2YG3ctvfN7w.7'
driver = '{ODBC Driver 18 for SQL Server}'

# Set up the connection
conn_str = (
    f"DRIVER={driver};"
    f"SERVER={server};"
    f"DATABASE={database};"
    f"UID={username};"
    f"PWD={password}"
)

# Connect to the database
conn = pyodbc.connect(conn_str)

# Create a cursor from the connection
cursor = conn.cursor()

# Fetch the schema information
# This example fetches table names and their columns
schema_query = """
SELECT 
    TABLE_SCHEMA, 
    TABLE_NAME, 
    COLUMN_NAME, 
    DATA_TYPE 
FROM 
    INFORMATION_SCHEMA.COLUMNS
ORDER BY 
    TABLE_SCHEMA, 
    TABLE_NAME, 
    ORDINAL_POSITION;
"""

cursor.execute(schema_query)

# Retrieve and print the schema information
for row in cursor.fetchall():
    print(row)

# Close the cursor and connection
cursor.close()
conn.close()
