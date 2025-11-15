import psycopg2


def add_user(conn: psycopg2.extensions.connection, username: str, password: str, role: str) -> tuple[str, str] | None:
    """
    Menambahkan user dari sisi admin
    :param conn:
    :param username:
    :param password:
    :param role:
    :return: tuple[str,str] | None
    """

    cursor = conn.cursor()
    while role not in ['petani', 'surveyor']:
        role = input("Ulangi pilihan (petani/surveyor): ").strip().lower()

    cursor.execute(f"SELECT * FROM {role} WHERE username = '{username}'")
    if cursor.fetchone():
        print("Username sudah ada.")
        return None

    cursor.execute(f"INSERT INTO {role} (username, password) VALUES ('{username}', '{password}') RETURNING *;")
    new_user = cursor.fetchone()
    conn.commit()
    cursor.close()
    return new_user
