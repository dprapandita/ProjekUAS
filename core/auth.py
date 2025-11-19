# import psycopg2
#
#
# def signup(conn: psycopg2.extensions.connection) -> None:
#     """
#     Logic untuk registrasi petani / surveyor
#     :param conn:
#     :return None:
#     """
#     print("Mendaftar user baru...")
#     role = None
#     while role not in ['surveyor', 'petani']:
#         role = input("Daftar sebagai (surveyor/petani): ").strip().lower()
#         if role not in ['surveyor', 'petani']:
#             print("Role harus 'surveyor' atau 'petani'.")
#
#     username = input("Username: ").strip()
#     password = input("Password: ").strip()
#
#     table = role  # aman karena role sudah divalidasi hanya ke dua nilai ini
#     cursor = conn.cursor()
#
#     cursor.execute(f"SELECT 1 FROM {table} WHERE username = %s", (username,))
#
#     if cursor.fetchone():
#         print("Username sudah terdaftar, coba username lain.")
#         cursor.close()
#         return
#
#     if input("Mau lanjut ke login? (y/n): ").strip().lower() == 'y':
#         login(conn)
#         return
#
#     user_query = f"INSERT INTO {table} (username, password) VALUES (%s, %s)"
#     cursor.execute(user_query, (username, password))
#     conn.commit()
#     cursor.close()
#     print(f"User {username} berhasil didaftarkan sebagai {role}.")
#
#
# def login(conn: psycopg2.extensions.connection) -> dict[str, str] | None:
#     """
#     Logic untuk login semua role (admin, petani, surveyor)
#     :param conn:
#     :return dict[str, str] | None:
#     """
#     print("Logging in...")
#     role = None
#     while role not in ['admin', 'surveyor', 'petani']:
#         role = input("Login sebagai (admin/surveyor/petani): ").strip().lower()
#         if role not in ['admin', 'surveyor', 'petani']:
#             print("Role harus salah satu dari: admin, surveyor, petani")
#
#     username = input("Username: ").strip()
#     password = input("Password: ").strip()
#
#     if role == 'admin':
#         table_name = 'admin'
#         id_field = 'admin_id'
#     elif role == 'surveyor':
#         table_name = 'surveyor'
#         id_field = 'surveyor_id'
#     else:
#         table_name = 'petani'
#         id_field = 'petani_id'
#
#     cursor = conn.cursor()
#     query = f"SELECT {id_field}, username FROM {table_name} WHERE username = %s AND password = %s;"
#     cursor.execute(query, (username, password))
#     result = cursor.fetchone()
#     cursor.close()
#     if result:
#         user = {
#             'id': result[0],
#             'username': username,
#             'role': role
#         }
#         print(f"Login berhasil! Anda masuk sebagai {role}: {username}")
#         return user
#     else:
#         print("Login gagal! Username atau password salah.")
#         return None
import psycopg2
from typing import Optional


def signup(conn: psycopg2.extensions.connection) -> None:
    """
    Registrasi user baru (petani / surveyor) ke tabel users + user_roles.
    """
    print("Mendaftar user baru...")
    role = None
    while role not in ["surveyor", "petani"]:
        role = input("Daftar sebagai (surveyor/petani): ").strip().lower()
        if role not in ["surveyor", "petani"]:
            print("Role harus 'surveyor' atau 'petani'.")

    name = input("Nama lengkap: ").strip()
    username = input("Username: ").strip()
    password = input("Password: ").strip()
    email = input("Email (boleh kosong): ").strip() or None
    no_telp = input("No. Telp (boleh kosong): ").strip() or None

    cur = conn.cursor()

    # Cek username sudah ada
    cur.execute("SELECT 1 FROM users WHERE username = %s", (username,))
    if cur.fetchone():
        print("Username sudah terdaftar, coba username lain.")
        cur.close()
        return

    # Ambil role_id dari tabel roles
    cur.execute(
        "SELECT role_id FROM roles WHERE LOWER(nama_role) = LOWER(%s)",
        (role,),
    )
    row = cur.fetchone()
    if not row:
        print(f"Role '{role}' belum ada di tabel roles.")
        cur.close()
        return
    role_id = row[0]

    # Insert ke users
    cur.execute(
        """
        INSERT INTO users (name, username, password, email, no_telp)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING user_id;
        """,
        (name, username, password, email, no_telp),
    )
    user_row = cur.fetchone()
    if not user_row:
        conn.rollback()
        cur.close()
        print("Gagal membuat user.")
        return

    user_id = user_row[0]

    # Mapping ke user_roles
    cur.execute(
        """
        INSERT INTO user_roles (id_user, id_role)
        VALUES (%s, %s)
        """,
        (user_id, role_id),
    )

    conn.commit()
    cur.close()
    print(f"User {username} berhasil didaftarkan sebagai {role}.")

    if input("Mau lanjut ke login? (y/n): ").strip().lower() == "y":
        login(conn)

def login(conn: psycopg2.extensions.connection) -> Optional[dict[str, str | int]]:
    """
    Login untuk admin / petani / surveyor berdasarkan tabel users + roles + user_roles.
    Return dict user jika berhasil, else None.
    """
    print("Logging in...")
    role = None
    while role not in ["admin", "surveyor", "petani"]:
        role = input("Login sebagai (admin/surveyor/petani): ").strip().lower()
        if role not in ["admin", "surveyor", "petani"]:
            print("Role harus salah satu dari: admin, surveyor, petani")

    username = input("Username: ").strip()
    password = input("Password: ").strip()

    cur = conn.cursor()
    # Cek user + password + role
    cur.execute(
        """
        SELECT
            u.user_id,
            u.username,
            u.name,
            r.nama_role
        FROM users u
        JOIN user_roles ur ON ur.id_user = u.user_id
        JOIN roles r       ON r.role_id = ur.id_role
        WHERE u.username = %s
          AND u.password = %s
          AND LOWER(r.nama_role) = LOWER(%s);
        """,
        (username, password, role),
    )

    row = cur.fetchone()
    cur.close()

    if row:
        user_id, username_db, name_db, role_db = row
        user = {
            "id": user_id,
            "username": username_db,
            "name": name_db,
            "role": role_db.lower(),  # konsisten dengan yang dipakai di fungsi lain
        }
        print(f"Login berhasil! Anda masuk sebagai {role_db}: {username_db}")
        return user
    else:
        print("Login gagal! Username/password/role tidak cocok.")
        return None
