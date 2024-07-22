import pyodbc
import os

# Define the connection string for the master database
server = 'localhost'  # or the server name/IP
database = 'master'  # Connect to master database to check and create toga database
username = 'SA'  # System Administrator username
password = 'V_p2YG3ctvfN7w.7'
driver = '{ODBC Driver 18 for SQL Server}'

# Define the database files location
mdf_file = '/home/toga-database/database/toga.mdf'
ndf_file = '/home/toga-database/database/ftrow_Documenten.ndf'
ldf_file = '/home/toga-database/database/toga_1.ldf'

# Set up the connection to the master database
conn_str = (
    f"DRIVER={driver};"
    f"SERVER={server};"
    f"DATABASE={database};"
    f"UID={username};"
    f"PWD={password};"
    f"Encrypt=no;"  # Disable encryption for simplicity
    f"TrustServerCertificate=yes;"  # Trust the server certificate
)

# Connect to the master database
conn = pyodbc.connect(conn_str)
cursor = conn.cursor()

# Check if the toga database exists
cursor.execute("SELECT name FROM sys.databases WHERE name = 'toga'")
database_exists = cursor.fetchone()

if not database_exists:
    # Database does not exist, create it
    print("Database 'toga' does not exist. Creating database...")
    attach_query = f"""
    CREATE DATABASE toga ON 
    (FILENAME = '{mdf_file}'),
    (FILENAME = '{ndf_file}'),
    (FILENAME = '{ldf_file}')
    FOR ATTACH;
    """
    cursor.execute(attach_query)
    conn.commit()
    print("Database 'toga' created successfully.")
else:
    print("Database 'toga' already exists.")

# Close the connection to the master database
cursor.close()
conn.close()

# Set up the connection to the toga database
conn_str = (
    f"DRIVER={driver};"
    f"SERVER={server};"
    f"DATABASE=toga;"
    f"UID={username};"
    f"PWD={password};"
    f"Encrypt=no;"  # Disable encryption for simplicity
    f"TrustServerCertificate=yes;"  # Trust the server certificate
)

# Connect to the toga database
conn = pyodbc.connect(conn_str)
cursor = conn.cursor()

# Fetch the schema information
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
