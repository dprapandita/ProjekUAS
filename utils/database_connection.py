import psycopg2

DB_CONFIG = {
    'host': 'localhost',
    'user': 'postgres',
    'password': '1234',
    'database': 'projekuas',
}


def get_connection():
    """
    Koneksi untuk database postgresql
    :return connection:
    """
    return psycopg2.connect(
        host=DB_CONFIG['host'],
        database=DB_CONFIG['database'],
        user=DB_CONFIG['user'],
        password=DB_CONFIG['password'],
    )
