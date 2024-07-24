import pyodbc
import argparse
import datetime as dt


def check_and_create_database(server, username, password, database, mdf_file, ndf_file, ldf_file):
    master_database = 'master'
    driver = '{ODBC Driver 18 for SQL Server}'

    conn_str = (
        f"DRIVER={driver};"
        f"SERVER={server};"
        f"DATABASE={master_database};"
        f"UID={username};"
        f"PWD={password};"
        f"Encrypt=no;"
        f"TrustServerCertificate=yes;"
    )

    conn = pyodbc.connect(conn_str, autocommit=True)
    cursor = conn.cursor()

    cursor.execute(f"SELECT name FROM sys.databases WHERE name = '{database}'")
    database_exists = cursor.fetchone()

    if not database_exists:
        print(f"Database '{database}' does not exist. Creating database...")
        attach_query = f"""
        CREATE DATABASE {database} ON 
        (FILENAME = '{mdf_file}'),
        (FILENAME = '{ndf_file}'),
        (FILENAME = '{ldf_file}')
        FOR ATTACH;
        """
        cursor.execute(attach_query)
        print(f"Database '{database}' created successfully.")
    else:
        print(f"Database '{database}' already exists.")

    cursor.close()
    conn.close()


def fetch_schema_information(server, username, password, database, output_file):
    driver = '{ODBC Driver 18 for SQL Server}'
    conn_str = (
        f"DRIVER={driver};"
        f"SERVER={server};"
        f"DATABASE={database};"
        f"UID={username};"
        f"PWD={password};"
        f"Encrypt=no;"
        f"TrustServerCertificate=yes;"
    )
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()

    schema_query = """
    SELECT TABLE_SCHEMA, TABLE_NAME, COLUMN_NAME, DATA_TYPE, IS_NULLABLE, CHARACTER_MAXIMUM_LENGTH
    FROM INFORMATION_SCHEMA.COLUMNS
    ORDER BY TABLE_SCHEMA, TABLE_NAME, ORDINAL_POSITION;
    """

    cursor.execute(schema_query)

    tables = {}
    with open(output_file, 'w') as f:
        current_table = None
        for row in cursor.fetchall():
            schema = {
                'table_schema': row.TABLE_SCHEMA,
                'table_name': row.TABLE_NAME,
                'column_name': row.COLUMN_NAME,
                'data_type': row.DATA_TYPE,
                'is_nullable': row.IS_NULLABLE,
                'character_maximum_length': row.CHARACTER_MAXIMUM_LENGTH
            }

            table_key = (schema['table_schema'], schema['table_name'])
            if table_key not in tables:
                tables[table_key] = []

            tables[table_key].append((schema['column_name'], schema['data_type']))

            if current_table != table_key:
                if current_table:
                    f.write(');\n\n')
                f.write(f"CREATE TABLE [{schema['table_schema']}].[{schema['table_name']}] (\n")
                current_table = table_key

            f.write(f"  [{schema['column_name']}] {schema['data_type']}")
            if schema['data_type'].upper() in ['VARCHAR', 'CHAR', 'NVARCHAR', 'NCHAR']:
                if schema['character_maximum_length'] and int(schema['character_maximum_length']) > 0:
                    f.write(f"({schema['character_maximum_length']})")
                else:
                    f.write("(MAX)")
            if schema['is_nullable'] == 'NO':
                f.write(" NOT NULL")
            f.write(",\n")

        if current_table:
            f.write(');\n')

        for (table_schema, table_name), columns in tables.items():
            column_list = ', '.join([f"[{col}]" for col, _ in columns])
            row_query = f"SELECT TOP 10 {column_list} FROM [{table_schema}].[{table_name}]"
            cursor.execute(row_query)
            rows = cursor.fetchall()

            f.write(f"\n-- Data for table [{table_schema}].[{table_name}]\n")
            for row in rows:
                row_data = []
                for value, (col_name, col_type) in zip(row, columns):
                    if value is None:
                        row_data.append('NULL')
                    elif col_type in ['int', 'decimal', 'float', 'money', 'numeric', 'real', 'smallint', 'tinyint']:
                        row_data.append(str(value))
                    elif col_type == 'bit':
                        row_data.append('1' if value else '0')
                    elif col_type in ['char', 'nchar', 'varchar', 'nvarchar']:
                        formatted_value = str(value).replace("'", "''")
                        row_data.append(f"'{formatted_value}'")
                    elif col_type in ['datetime', 'smalldatetime', 'date', 'time', 'datetime2']:
                        # Format datetime values to ISO 8601 format
                        if isinstance(value, dt.datetime):
                            formatted_value = value.strftime('%Y%m%dT%H:%M:%S')
                            row_data.append(f"'{formatted_value}'")
                        elif isinstance(value, dt.date):
                            formatted_value = value.strftime('%Y%m%d')
                            row_data.append(f"'{formatted_value}'")
                        elif isinstance(value, dt.time):
                            formatted_value = value.strftime('%H:%M:%S')
                            row_data.append(f"'{formatted_value}'")
                    else:
                        formatted_value = str(value).replace("'", "''")
                        row_data.append(f"'{formatted_value}'")  # Default case for strings and other types

                row_data_joined = ", ".join(row_data)
                f.write(f"INSERT INTO [{table_schema}].[{table_name}] ({column_list}) VALUES ({row_data_joined});\n")

    print(f"Schema information with sample data exported to '{output_file}'.")

    cursor.close()
    conn.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Check and create a SQL Server database if it does not exist, and fetch its schema.')
    parser.add_argument('-s', dest='server', required=True, help='The SQL Server name or IP address')
    parser.add_argument('-u', dest='username', required=True, help='The SQL Server username')
    parser.add_argument('-p', dest='password', required=True, help='The SQL Server password')
    parser.add_argument('-db', dest='database', required=True, help='The SQL database')
    parser.add_argument('-mdf', dest='mdf_file', required=True, help='The primary database file (.mdf)')
    parser.add_argument('-ndf', dest='ndf_file', required=True, help='The secondary database file (.ndf)')
    parser.add_argument('-ldf', dest='ldf_file', required=True, help='The log database file (.ldf)')
    parser.add_argument('-o', dest='output_file', required=True,
                        help='The output SQL file to save the schema information')

    args = parser.parse_args()

    check_and_create_database(args.server, args.username, args.password, args.database, args.mdf_file, args.ndf_file,
                              args.ldf_file)
    fetch_schema_information(args.server, args.username, args.password, args.database, args.output_file)
