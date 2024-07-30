import argparse
import pyodbc
import xmlrpc.client


def parse_arguments():
    parser = argparse.ArgumentParser(description='Migrate data from a SQL Server database to Odoo')
    parser.add_argument('-ts', dest='toga_server', required=True, help='The Toga SQL Server name or IP address')
    parser.add_argument('-tu', dest='toga_username', required=True, help='The Toga SQL Server username')
    parser.add_argument('-tp', dest='toga_password', required=True, help='The Toga SQL Server password')
    parser.add_argument('-tdb', dest='toga_database', required=True, help='The Toga SQL database')
    parser.add_argument("-d", dest="odbc_driver", required=True, help="The driver used by pyodbc")
    parser.add_argument("-ourl", dest="odoo_url", required=True, help="Odoo URL")
    parser.add_argument("-odb", dest="odoo_db", required=True, help="Odoo Database Name")
    parser.add_argument("-ou", dest="odoo_user", required=True, help="Odoo User Name")
    parser.add_argument("-os", dest="odoo_secret", required=True, help="Odoo Password or API Key")
    return parser.parse_args()


def connect_sql_server(args):
    conn_str = (
        f"DRIVER={args.odbc_driver};"
        f"SERVER={args.toga_server};"
        f"DATABASE={args.toga_database};"
        f"UID={args.toga_username};"
        f"PWD={args.toga_password};"
        f"TrustServerCertificate=yes;"
    )
    return pyodbc.connect(conn_str)


def connect_odoo(args):
    common = xmlrpc.client.ServerProxy(f"{args.odoo_url}/xmlrpc/2/common")
    uid = common.authenticate(args.odoo_db, args.odoo_user, args.odoo_secret, {})
    models = xmlrpc.client.ServerProxy(f"{args.odoo_url}/xmlrpc/2/object", allow_none=True)
    return uid, models


def fetch_contacts(cursor):
    # Join kon1 and kon2 to fetch complete contact information
    query = """
    SELECT kon1.koref, kon1.nm, kon1.vnm, kon1.strt, kon1.plts, kon1.lnd, 
           kon2.tel, kon2.email, kon1.iban, kon1.bic 
    FROM kon1
    LEFT JOIN kon2 ON kon1.koref = kon2.koref
    """
    cursor.execute(query)
    return cursor.fetchall()


def fetch_cases(cursor):
    cursor.execute("SELECT ino, dosno, dosnm FROM doss")
    return cursor.fetchall()


def fetch_links(cursor):
    cursor.execute("SELECT ino, koref, contactid FROM kodo")
    return cursor.fetchall()


def create_odoo_contacts(contacts, uid, models, args):
    contact_data = []
    contact_mapping = {}
    for contact in contacts:
        koref, nm, vnm, strt, plts, lnd, tel, email, iban, bic = contact
        contact_data.append({
            'name': f"{nm} {vnm}",
            'street': strt,
            'city': plts,
            # 'country_id': lnd,  # This might need to be adjusted to match Odoo's country data
            'phone': tel,
            'email': email,
            # 'iban': iban,
            # 'bic': bic
        })

    contact_ids = models.execute_kw(args.odoo_db, uid, args.odoo_secret,
                                    'res.partner', 'create', [contact_data])

    for i, contact_id in enumerate(contact_ids):
        contact_mapping[contacts[i][0]] = contact_id

    return contact_mapping


def create_odoo_cases(cases, uid, models, args):
    case_data = []
    case_mapping = {}
    for case in cases:
        ino, dosno, dosnm = case
        case_data.append({
            'name': dosnm,
        })

    case_ids = models.execute_kw(args.odoo_db, uid, args.odoo_secret,
                                 'cases.case', 'create', [case_data])

    for i, case_id in enumerate(case_ids):
        case_mapping[cases[i][0]] = case_id

    return case_mapping


def create_links(links, case_mapping, contact_mapping, uid, models, args):
    link_data = []
    for link in links:
        ino, koref, contactid = link
        if ino in case_mapping and koref in contact_mapping:
            link_data.append({
                'case_id': case_mapping[ino],
                'partner_id': contact_mapping[koref]
            })

    models.execute_kw(args.odoo_db, uid, args.odoo_secret,
                      'cases.party', 'create', [link_data])


if __name__ == "__main__":
    # Set up argument parsing
    args = parse_arguments()

    # Connect to SQL Server
    conn = connect_sql_server(args)
    cursor = conn.cursor()

    # Connect to Odoo
    uid, models = connect_odoo(args)

    # Fetch and create contacts in Odoo
    contacts = fetch_contacts(cursor)
    contact_mapping = create_odoo_contacts(contacts, uid, models, args)

    # Fetch and create cases in Odoo
    cases = fetch_cases(cursor)
    case_mapping = create_odoo_cases(cases, uid, models, args)

    # Fetch and create links between contacts and cases in Odoo
    links = fetch_links(cursor)
    create_links(links, case_mapping, contact_mapping, uid, models, args)

    # Close the cursor and connection
    cursor.close()
    conn.close()
