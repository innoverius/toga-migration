import pyodbc
import argparse


def check_and_create_database(server, username, password, mdf_file, ndf_file, ldf_file):
    # Define the connection string for the master database
    database = 'master'  # Connect to master database to check and create toga database
    driver = '{ODBC Driver 18 for SQL Server}'

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

    # Connect to the master database with autocommit
    conn = pyodbc.connect(conn_str, autocommit=True)
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
        print("Database 'toga' created successfully.")
    else:
        print("Database 'toga' already exists.")

    # Close the connection to the master database
    cursor.close()
    conn.close()


def fetch_schema_information(server, username, password, database):
    driver = '{ODBC Driver 18 for SQL Server}'

    # Set up the connection to the toga database
    conn_str = (
        f"DRIVER={driver};"
        f"SERVER={server};"
        f"DATABASE={database};"
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


if __name__ == "__main__":
    # Set up argument parsing
    parser = argparse.ArgumentParser(description='Check and create a SQL Server database if it does not exist, and fetch its schema.')
    parser.add_argument('-s', dest='server', required=True, help='The SQL Server name or IP address')
    parser.add_argument('-u', dest='username', required=True, help='The SQL Server username')
    parser.add_argument('-p', dest='password', required=True, help='The SQL Server password')
    parser.add_argument('-db', dest='database', required=True, help='The SQL database')
    parser.add_argument('-mdf', dest='mdf_file', required=True, help='The primary database file (.mdf)')
    parser.add_argument('-ndf', dest='ndf_file', required=True, help='The secondary database file (.ndf)')
    parser.add_argument('-ldf', dest='ldf_file', required=True, help='The log database file (.ldf)')

    args = parser.parse_args()

    check_and_create_database(args.server, args.username, args.password, args.mdf_file, args.ndf_file, args.ldf_file)
    fetch_schema_information(args.server, args.username, args.password, args.database)
