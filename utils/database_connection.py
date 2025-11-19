import psycopg2

DB_CONFIG = {
    'host': 'localhost',
    'user': 'postgres',
    'password': '23',
    'database': 'ProjekUAS',
}


def get_connection():
    """
    Koneksi untuk database postgresql
    :return connection:
    """
    try:

        return psycopg2.connect(
            host=DB_CONFIG['host'],
            database=DB_CONFIG['database'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
        )
    except psycopg2.Error as e :
        print("Gagal koneksi ke database:", e)
        exit(1)
