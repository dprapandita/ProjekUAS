from typing import Any, Optional

import psycopg2


def add_user(
        conn,
        name: str,
        username: str,
        password: str,
        role_name: str,
        email: str | None = None,
        no_telp: str | None = None,
) -> Optional[tuple[int, str, str]]:
    """
    Tambah user baru ke tabel users + set role di user_roles.
    :return: (user_id, username, role_name) atau None jika username sudah ada / role tidak ditemukan.
    """
    with conn.cursor() as cur:
        # Cek username sudah ada atau belum
        cur.execute("SELECT 1 FROM users WHERE username = %s", (username,))
        if cur.fetchone():
            print("Username sudah ada.")
            return None

        # Ambil role_id
        cur.execute(
            "SELECT role_id FROM roles WHERE LOWER(nama_role) = LOWER(%s)",
            (role_name,),
        )
        role_row = cur.fetchone()
        if not role_row:
            print(f"Role '{role_name}' tidak ditemukan di tabel roles.")
            return None
        role_id = role_row[0]

        # Insert ke users
        cur.execute(
            """
            INSERT INTO users (name, username, password, email, no_telp)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING user_id, username;
            """,
            (name, username, password, email, no_telp),
        )
        user_row = cur.fetchone()
        if not user_row:
            conn.rollback()
            return None
        user_id, username_db = user_row

        # Insert ke user_roles
        cur.execute(
            """
            INSERT INTO user_roles (id_user, id_role)
            VALUES (%s, %s)
            """,
            (user_id, role_id),
        )

        conn.commit()
        print(f"User {username_db} dengan role {role_name} berhasil dibuat.")
        return user_id, username_db, role_name


def get_user_by_id(conn: psycopg2.extensions.connection, user_id: int) -> Optional[dict[str, Any]]:
    """
        Ambil data user dari tabel users berdasarkan user_id.
        """
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT user_id, name, username, email, no_telp, id_alamat
            FROM users
            WHERE user_id = %s
            """,
            (user_id,),
        )
        row = cur.fetchone()

    if not row:
        return None

    return {
        "user_id": row[0],
        "name": row[1],
        "username": row[2],
        "email": row[3],
        "no_telp": row[4],
        "id_alamat": row[5],
    }


def delete_user(
        conn,
        username: str,
        role_name: str | None = None,
) -> Optional[int]:
    """
    Hapus user berdasarkan username.
    Jika role_name diisi, pastikan user punya role tsb dulu.
    Return: user_id yang terhapus atau None.
    """
    with conn.cursor() as cur:
        if role_name:
            # Pastikan user dengan role tertentu
            cur.execute(
                """
                SELECT u.user_id
                FROM users u
                JOIN user_roles ur ON ur.id_user = u.user_id
                JOIN roles r       ON r.role_id = ur.id_role
                WHERE u.username = %s
                  AND LOWER(r.nama_role) = LOWER(%s)
                """,
                (username, role_name),
            )
        else:
            # Hanya berdasarkan username
            cur.execute(
                "SELECT user_id FROM users WHERE username = %s",
                (username,),
            )

        row = cur.fetchone()
        if not row:
            print(f"User '{username}' tidak ditemukan.")
            return None

        user_id = row[0]

        # Hapus dulu dari user_roles (FK)
        cur.execute("DELETE FROM user_roles WHERE id_user = %s", (user_id,))
        # Hapus dari users
        cur.execute(
            "DELETE FROM users WHERE user_id = %s RETURNING user_id;",
            (user_id,),
        )
        deleted = cur.fetchone()
        conn.commit()
        print(f"User '{username}' terhapus.")
        return deleted[0] if deleted else None


def read_all_users(conn: psycopg2.extensions.connection) -> dict[str, list[tuple[Any, ...]]]:
    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT r.nama_role, u.user_id, u.name, u.username
            FROM users u
            JOIN user_roles ur ON ur.id_user = u.user_id
            JOIN roles r       ON r.role_id = ur.id_role
            ORDER BY r.nama_role, u.user_id;
            """)
        rows = cursor.fetchall()

    result = {}
    for nama_role, user_id, name, username in rows:
        key = nama_role.lower()
        result.setdefault(key, []).append((user_id, name, username))
    return result

def update_user_profile(
    conn: psycopg2.extensions.connection,
    user_id: int,
    *,
    name: Optional[str] = None,
    email: Optional[str] = None,
    no_telp: Optional[str] = None,
    password: Optional[str] = None,
    id_alamat: Optional[int] = None,
) -> bool:
    """
    Update profil user di tabel users.
    Field yang None tidak akan di-update.
    Return True kalau ada baris yang berubah.
    """
    fields = []
    values: list[Any] = []

    if name is not None:
        fields.append("name = %s")
        values.append(name)

    if email is not None:
        fields.append("email = %s")
        values.append(email)

    if no_telp is not None:
        fields.append("no_telp = %s")
        values.append(no_telp)

    if password is not None:
        fields.append("password = %s")
        values.append(password)

    if id_alamat is not None:
        fields.append("id_alamat = %s")
        values.append(id_alamat)

    # kalau gak ada yang mau diupdate, langsung balik
    if not fields:
        print("Tidak ada data yang diubah.")
        return False

    values.append(user_id)

    query = f"""
        UPDATE users
        SET {", ".join(fields)}
        WHERE user_id = %s
    """

    with conn.cursor() as cur:
        cur.execute(query, tuple(values))
        conn.commit()
        return cur.rowcount > 0


def lihat_data_lahan(conn) -> dict[str, Any]:
    """
    Ambil overview data:
    - user yang berperan sebagai petani
    - semua lahan + alamat + surveyor + petani
    - semua survey_data + info iklim, tanah, tanaman + petani
    """
    cursor = conn.cursor()

    # 1. Ambil semua user yang punya role 'petani'
    cursor.execute(
        """
        SELECT
            u.user_id,
            u.name,
            u.username,
            u.email,
            u.no_telp
        FROM users u
        JOIN user_roles ur ON ur.id_user = u.user_id
        JOIN roles r       ON r.role_id = ur.id_role
        WHERE LOWER(r.nama_role) = 'petani'
        ORDER BY u.user_id;
        """
    )
    petani = cursor.fetchall()

    # 2. Ambil semua lahan + petani + surveyor + alamat
    cursor.execute(
        """
        SELECT
            l.lahan_id,
            l.ketinggian,

            u_p.user_id        AS petani_id,
            u_p.name           AS nama_petani,

            u_s.user_id        AS surveyor_id,
            u_s.name           AS nama_surveyor,

            a.alamat_id,
            a.nama_jalan,
            kc.nama_kecamatan,
            k.nama_kota,
            p.nama_provinsi
        FROM lahan l
        LEFT JOIN users u_p       ON u_p.user_id    = l.id_user_petani
        LEFT JOIN users u_s       ON u_s.user_id    = l.id_user_surveyor
        LEFT JOIN alamat a        ON a.alamat_id    = l.id_alamat
        LEFT JOIN kecamatan kc    ON kc.kecamatan_id = a.id_kecamatan
        LEFT JOIN kota k          ON k.kota_id      = a.id_kota
        LEFT JOIN provinsi p      ON p.provinsi_id  = a.id_provinsi
        ORDER BY l.lahan_id;
        """
    )
    lahan = cursor.fetchall()

    # 3. Ambil semua survey_data + iklim + tanah + tanaman + petani (via lahan)
    cursor.execute(
        """
        SELECT
            sd.survey_id,
            sd.id_lahan,

            sd.id_user_surveyor,
            us.name               AS nama_surveyor,

            sd.id_user_admin,
            ua.name               AS nama_admin,

            sd.status_survey,
            sd.tanggal_survey,

            sd.id_iklim,
            ik.jenis_cuaca,

            sd.id_tanah,
            kt.kondisi_tanah,
            kt.ph,
            kt.kandungan_nutrisi,
            kt.kelembapan,

            sd.id_tanaman,
            t.nama                AS nama_tanaman,

            u_p.user_id           AS petani_id,
            u_p.name              AS nama_petani
        FROM survey_data sd
        LEFT JOIN users us          ON us.user_id = sd.id_user_surveyor
        LEFT JOIN users ua          ON ua.user_id = sd.id_user_admin
        LEFT JOIN iklim ik          ON ik.iklim_id = sd.id_iklim
        LEFT JOIN kondisi_tanah kt  ON kt.kondisi_tanah_id = sd.id_tanah
        LEFT JOIN tanaman t         ON t.tanaman_id = sd.id_tanaman
        LEFT JOIN lahan l           ON l.lahan_id = sd.id_lahan
        LEFT JOIN users u_p         ON u_p.user_id = l.id_user_petani
        ORDER BY sd.survey_id;
        """
    )
    survey_data = cursor.fetchall()

    cursor.close()

    return {
        "petani": petani,
        "lahan": lahan,
        "survey_data": survey_data,
    }
