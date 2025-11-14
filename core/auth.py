import psycopg2


def signup(conn: psycopg2.extensions.connection) -> None:
    """
    Logic untuk registrasi petani / surveyor
    :param conn:
    :return None:
    """
    print("Signing in ...")
    role = None
    while role not in ['surveyor', 'petani']:
        role = input("Daftar sebagai (surveyor/petani): ").strip().lower()
        if role not in ['surveyor', 'petani']:
            print("Role harus 'surveyor' atau 'petani'.")

    username = input("Username: ").strip()
    password = input("Password: ").strip()

    table = role
    cursor = conn.cursor()

    cursor.execute(f"SELECT * FROM {table} WHERE username = %s", (username,))

    if cursor.fetchone():
        print("Username sudah terdaftar, coba username lain.")
        cursor.close()
        return

    user_query = f"INSERT INTO {table} (username, password) VALUES ('{username}', '{password}')"
    cursor.execute(user_query, (username, password))
    conn.commit()
    cursor.close()
    print(f"User {username} berhasil didaftarkan sebagai {role}.")


def login(conn: psycopg2.extensions.connection) -> dict[str, str] | None:
    """
    Logic untuk login semua role (admin, petani, surveyor)
    :param conn:
    :return dict[str, str] | None:
    """
    print("Logging in...")
    role = None
    while role not in ['admin', 'surveyor', 'petani']:
        role = input("Login sebagai (admin/surveyor/petani): ").strip().lower()
        if role not in ['admin', 'surveyor', 'petani']:
            print("Role harus salah satu dari: admin, surveyor, petani")

    username = input("Username: ").strip()
    password = input("Password: ").strip()

    if role == 'admin':
        table_name = 'admin'
        id_field = 'admin_id'
    elif role == 'surveyor':
        table_name = 'surveyor'
        id_field = 'surveyor_id'
    else:
        table_name = 'petani'
        id_field = 'petani_id'

    cursor = conn.cursor()
    query = f"SELECT {id_field}, username FROM {table_name} WHERE username = '{username}' AND password = '{password}';"
    cursor.execute(query)
    result = cursor.fetchone()
    cursor.close()
    if result:
        print(result)
        user = {
            'id': result[0],
            'username': username,
            'role': role
        }
        print(f"Login berhasil! Anda masuk sebagai {role}: {username}")
        return user
    else:
        print("Login gagal! Username atau password salah.")
        return None
