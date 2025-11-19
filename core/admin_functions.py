from typing import Any, Optional

import psycopg2


def add_user(
    conn: psycopg2.extensions.connection,
    username: str,
    password: str,
    role: str,
) -> Optional[tuple[Any, ...]]:
    """
    Menambahkan user dari sisi admin
    :param conn:
    :param username:
    :param password:
    :param role:
    :return: tuple[str,str] | None
    """

    if role not in ["petani", "surveyor"]:
        raise ValueError("Role harus 'petani' atau 'surveyor'.")

    id_field = f"{role}_id"

    with conn.cursor() as cursor:
        cursor.execute(f"SELECT 1 FROM {role} WHERE username = %s", (username,))
        if cursor.fetchone():
            print("Username sudah ada.")
            return None

        cursor.execute(
            f"INSERT INTO {role} (username, password) VALUES (%s, %s) RETURNING {id_field}, username",
            (username, password),
        )
        new_user = cursor.fetchone()
        conn.commit()
        return new_user

def delete_user(
    conn: psycopg2.extensions.connection, username: str, role: str
) -> Optional[int]:
    role = role.strip().lower()
    if role not in ["petani", "surveyor"]:
        raise ValueError("Role tidak valid. Gunakan 'petani' atau 'surveyor'.")

    id_field = f"{role}_id"

    with conn.cursor() as cursor:
        cursor.execute(f"SELECT {id_field} FROM {role} WHERE username = %s", (username,))
        row = cursor.fetchone()
        if not row:
            print(f"Username {username} tidak ditemukan pada role {role}.")
            return None

        cursor.execute(
            f"DELETE FROM {role} WHERE username = %s RETURNING {id_field}", (username,)
        )
        deleted = cursor.fetchone()
        conn.commit()
        return deleted[0] if deleted else None


def read_all_users(conn: psycopg2.extensions.connection) -> dict[str, list[tuple[Any, ...]]]:
    cursor = conn.cursor()

    cursor.execute("SELECT petani_id, username FROM petani")
    petani = cursor.fetchall()

    cursor.execute("SELECT surveyor_id, username FROM surveyor")
    surveyor = cursor.fetchall()

    cursor.close()

    return {
        "petani": petani,
        "surveyor": surveyor,
    }

def lihat_data_lahan(conn: psycopg2.extensions.connection) -> dict[str, Any]:
    cursor = conn.cursor()

    cursor.execute("SELECT petani_id, username FROM petani")
    petani = cursor.fetchall()

    cursor.execute(
        "SELECT lahan_id, petani_id, tanah, ketinggian, iklim, tanggal_input FROM lahan"
    )
    lahan = cursor.fetchall()

    cursor.execute(
        "SELECT survey_id, lahan_id, surveyor_id, hasil_survey, tanggal_survey FROM survey_data"
    )
    survey_data = cursor.fetchall()

    cursor.close()

    return {
        "petani": petani,
        "lahan": lahan,
        "survey_data": survey_data,
    }
