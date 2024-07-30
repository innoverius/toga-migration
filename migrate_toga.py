import pyodbc
import argparse



def parse_arguments():
    parser = argparse.ArgumentParser(
        description='Check and create a SQL Server database if it does not exist, and fetch its schema.')
    parser.add_argument('-ts', dest='toga_server', required=True, help='The Toga SQL Server name or IP address')
    parser.add_argument('-tu', dest='toga_username', required=True, help='The Toga SQL Server username')
    parser.add_argument('-tp', dest='toga_password', required=True, help='The Toga SQL Server password')
    parser.add_argument('-tdb', dest='toga_database', required=True, help='The Toga SQL database')
    parser.add_argument("-d", dest="ODBC Driver", required=True, help="The driver used by pyodbc")
    parser.add_argument("-ourl", dest="odoo_url", required=True, help="Url of the Odoo database")
    parser.add_argument("-odb", dest="odoo_db", required=True, help="Name of the Odoo database")
    parser.add_argument("-ou", dest="odoo_user", required=True, help="Odoo user name")
    parser.add_argument("-os", dest="odoo_secret", required=True, help="Odoo user password or API key")
    return parser.parse_args()


if __name__ == "__main__":
    # Set up argument parsing
    args = parse_arguments()
