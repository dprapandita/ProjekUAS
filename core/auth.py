import psycopg2
from typing import Optional

from utils.address import pilih_alamat_baru
from utils.menus import menu_admin, menu_petani, menu_surveyor


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
    isi_alamat = input("Input alamat mu sekarang? (y/n): ").strip().lower()
    id_alamat = None
    if isi_alamat == "y":
        id_alamat = pilih_alamat_baru(conn)

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
        INSERT INTO users (name, username, password, email, no_telp, id_alamat)
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING user_id;
        """,
        (name, username, password, email, no_telp, id_alamat),
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
        user = login(conn)
        if user:
            role = user["role"]
            if role == "admin":
                menu_admin(conn, user)
            elif role == "petani":
                menu_petani(conn, user)
            elif role == "surveyor":
                menu_surveyor(conn, user)

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
