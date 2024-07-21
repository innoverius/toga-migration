import pyodbc


def initial_test():
    # Connection details
    server = 'localhost'
    username = 'SA'
    password = 'V_p2YG3ctvfN7w.7'
    original_db_mdf_path = '/home/toga-database/database/toga.mdf'
    original_db_name = 'toga'
    new_db_name = 'emptytoga'

    # Connection string
    connection_string = f'DRIVER={{ODBC Driver 18 for SQL Server}};SERVER={server};UID={username};PWD={password};TrustServerCertificate=yes'

    # Function to execute a query without a transaction
    def execute_query_without_transaction(query):
        conn = pyodbc.connect(connection_string, autocommit=True)
        cursor = conn.cursor()
        cursor.execute(query)
        cursor.close()
        conn.close()

    # Connect to SQL Server
    conn = pyodbc.connect(connection_string)
    cursor = conn.cursor()

    try:
        # Attach the original database
        attach_db_query = f"CREATE DATABASE {original_db_name} ON (FILENAME = '{original_db_mdf_path}') FOR ATTACH"
        execute_query_without_transaction(attach_db_query)
        print(f"Database {original_db_name} attached successfully.")

        # Generate the schema script
        schema_script = f"{original_db_name}_schema.sql"
        with open(schema_script, 'w') as f:
            cursor.execute(f"EXEC sp_MSforeachtable 'PRINT ''DROP TABLE ?''; SELECT * FROM sys.tables WHERE name = ?'")
            for row in cursor:
                f.write(f"{row[0]}\n")

        # Create a new empty database
        create_db_query = f"CREATE DATABASE {new_db_name}"
        execute_query_without_transaction(create_db_query)
        print(f"Database {new_db_name} created successfully.")

        # Apply the schema script to the new database
        with open(schema_script, 'r') as f:
            schema_sql = f.read()
            cursor.execute(f"USE {new_db_name}; {schema_sql}")
            conn.commit()
        print(f"Schema applied to {new_db_name} successfully.")

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        try:
            # Detach the original database if needed
            detach_db_query = f"EXEC sp_detach_db '{original_db_name}'"
            execute_query_without_transaction(detach_db_query)
            print(f"Database {original_db_name} detached successfully.")
        except Exception as e:
            print(f"An error occurred during detachment: {e}")

        cursor.close()
        conn.close()


if __name__ == '__main__':
    initial_test()
