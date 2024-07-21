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

    # Function to check if a database exists
    def check_database_exists(db_name):
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()
        cursor.execute(f"SELECT name FROM master.sys.databases WHERE name = '{db_name}'")
        db_exists = cursor.fetchone() is not None
        cursor.close()
        conn.close()
        return db_exists

    # Function to drop a database if it exists
    def drop_database_if_exists(db_name):
        if check_database_exists(db_name):
            drop_db_query = f"DROP DATABASE [{db_name}]"
            execute_query_without_transaction(drop_db_query)
            print(f"Database {db_name} dropped successfully.")

    # Function to generate the schema script for a database
    def generate_schema_script(db_name, schema_file):
        schema_script_query = f"USE {db_name}; EXEC sp_MSforeachtable @command1='PRINT ''DROP TABLE ?''; SELECT * FROM sys.tables WHERE name = ''''?'"
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()
        with open(schema_file, 'w') as f:
            cursor.execute(schema_script_query)
            for row in cursor:
                f.write(f"{row[0]}\n")
        cursor.close()
        conn.close()

    # Main logic
    try:
        # Generate the schema script
        schema_script = f"{original_db_name}_schema.sql"
        generate_schema_script(original_db_name, schema_script)
        print(f"Schema script for {original_db_name} generated successfully.")

        # Drop the new database if it exists
        # drop_database_if_exists(new_db_name)

        # Create a new empty database
        create_db_query = f"CREATE DATABASE {new_db_name}"
        execute_query_without_transaction(create_db_query)
        print(f"Database {new_db_name} created successfully.")

        # Apply the schema script to the new database
        with open(schema_script, 'r') as f:
            schema_sql = f.read()
            conn = pyodbc.connect(connection_string)
            cursor = conn.cursor()
            cursor.execute(f"USE {new_db_name}; {schema_sql}")
            conn.commit()
            cursor.close()
            conn.close()
        print(f"Schema applied to {new_db_name} successfully.")

    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == '__main__':
    initial_test()
