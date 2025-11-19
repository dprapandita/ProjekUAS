from datetime import date
from typing import Optional, Any


def input_angka(prompt, tipe=float) -> float | int:
    """
    Inputan angka dengan tipe berubah-ubah
    :param prompt:
    :param tipe:
    :return float | int:
    """
    while True:
        nilai = input(prompt).strip()
        try:
            return tipe(nilai)
        except (ValueError, AttributeError):
            print("Input harus angka, coba lagi.\n")

def add_lahan(
        conn, petani_id: int, ketinggian: float, tanah: str, iklim: str
) -> Optional[int]:
    """
    Inputan lahan
    :param conn:
    :param petani_id:
    :param ketinggian:
    :param tanah:
    :param iklim:
    :return tuple[str] | None:
    """
    tanggal = date.today()

    query = (
        "INSERT INTO lahan(petani_id, ketinggian, tanah, iklim, tanggal_input) "
        "VALUES (%s, %s, %s, %s, %s) RETURNING lahan_id;"
    )
    with conn.cursor() as cursor:
        cursor.execute(query, (petani_id, ketinggian, tanah, iklim, tanggal))
        row = cursor.fetchone()
        conn.commit()
        return row[0] if row else None

def lihat_lahan_universal(
    conn,
    user: dict[str, Any],
) -> list[tuple[Any, ...]] | None:
    """
    Ambil data lahan tergantung role:
    - petani   → lahan milik petani itu sendiri
    - surveyor → lahan yang pernah dia survey
    """
    role = user["role"]
    user_id = user["id"]

    cursor = conn.cursor()

    if role == "petani":
        # lahan milik petani ini saja
        cursor.execute(
            """
            SELECT
                l.lahan_id,
                p.username AS nama_petani,
                l.tanah,
                l.ketinggian,
                l.iklim,
                l.tanggal_input
            FROM lahan l
            JOIN petani p ON p.petani_id = l.petani_id
            WHERE l.petani_id = %s
            ORDER BY l.lahan_id;
            """,
            (user_id,)
        )

    elif role == "surveyor":
        # lahan yang pernah disurvey oleh surveyor ini
        cursor.execute(
            """
            SELECT DISTINCT
                l.lahan_id,
                p.username AS nama_petani,
                l.tanah,
                l.ketinggian,
                l.iklim,
                l.tanggal_input
            FROM survey_data sd
            JOIN lahan l
                ON l.lahan_id = sd.lahan_id
            LEFT JOIN petani p
                ON p.petani_id = l.petani_id
            WHERE sd.surveyor_id = %s
            ORDER BY l.lahan_id;
            """,
            (user_id,)
        )

    else:
        cursor.close()
        print(f"Role '{role}' gada")

    rows = cursor.fetchall()
    cursor.close()

    print("\n=== Daftar Lahan ===")
    if not rows:
        print("\nMasih kosong  ")
    for lahan_id, nama_petani, tanah, ketinggian, iklim, tanggal in rows:
        print(
            f"- ID: {lahan_id} | Petani: {nama_petani} | Tanah: {tanah} | "
            f"Ketinggian: {ketinggian} | Iklim: {iklim} | Tgl: {tanggal}"
        )


def add_tanaman(conn, nama_tanaman, deskripsi) -> Optional[int]:
    """
    Inputan tanaman
    :param conn:
    :param nama_tanaman:
    :param deskripsi:
    :return tuple[str, str] | None:
    """
    with conn.cursor() as cursor:
        # Cek eksistensi case-insensitive
        cursor.execute("SELECT 1 FROM tanaman WHERE LOWER(nama) = LOWER(%s)", (nama_tanaman,))
        if cursor.fetchone():
            print(f"nama tanaman {nama_tanaman} sudah ada")
            return None

        cursor.execute(
            "INSERT INTO tanaman (nama, deskripsi) VALUES (%s, %s) RETURNING tanaman_id;",
            (nama_tanaman, deskripsi),
        )
        row = cursor.fetchone()
        conn.commit()
        tanaman_id = row[0] if row else None
        if tanaman_id is not None:
            print(f"nama tanaman {nama_tanaman} dengan deskripsi {deskripsi} sudah masuk")
        return tanaman_id

def add_survey_data(
    conn,
    lahan_id: int,
    surveyor_id: int,
    hasil_survey: str
) -> Optional[int]:
    """
    Tambah data survey untuk suatu lahan oleh surveyor tertentu.
    """
    tanggal = date.today()

    query = """
        INSERT INTO survey_data (
            lahan_id,
            surveyor_id,
            hasil_survey,
            tanggal_survey
        ) VALUES (%s, %s, %s, %s)
        RETURNING survey_id;
    """

    cursor = conn.cursor()
    cursor.execute(
        query,
        (lahan_id, surveyor_id, hasil_survey, tanggal)
    )
    row = cursor.fetchone()
    conn.commit()
    cursor.close()

    return row[0] if row else None


def analysis_tanaman_dengan_lahan(conn) -> list[tuple[str, str]]:
    """
    Menggabungkan data lahan + hasil survey + tanaman yang ditanam.
    Bisa dipanggil dari menu admin atau surveyor untuk melihat overview.

    Return: list of tuple hasil query.
    """

    query = """
        SELECT
            l.lahan_id,
            p.petani_id,
            p.username         AS nama_petani,
            l.tanah,
            l.ketinggian,
            l.iklim,
            l.tanggal_input,

            sd.survey_id,
            sd.surveyor_id,
            s.username         AS nama_surveyor,
            sd.hasil_survey,
            sd.tanggal_survey,

            t.tanaman_id,
            t.nama             AS nama_tanaman,
            t.deskripsi        AS deskripsi_tanaman

        FROM lahan l
        JOIN petani p
            ON p.petani_id = l.petani_id
        LEFT JOIN survey_data sd
            ON sd.lahan_id = l.lahan_id
        LEFT JOIN surveyor s
            ON s.surveyor_id = sd.surveyor_id
        LEFT JOIN penanaman pn
            ON pn.lahan_id = l.lahan_id
        LEFT JOIN tanaman t
            ON t.tanaman_id = pn.tanaman_id
        ORDER BY l.lahan_id, sd.survey_id, t.tanaman_id;
    """

    cursor = conn.cursor()
    cursor.execute(query)
    rows = cursor.fetchall()
    cursor.close()

    # Optional: langsung print biar kelihatan di CLI
    if not rows:
        print("\nBelum ada data analisis lahan + tanaman.")
    else:
        print("\n=== HASIL ANALISIS LAHAN + TANAMAN ===")
        for row in rows:
            (
                lahan_id,
                petani_id,
                nama_petani,
                tanah,
                ketinggian,
                iklim,
                tanggal_input,
                survey_id,
                surveyor_id,
                nama_surveyor,
                hasil_survey,
                tanggal_survey,
                tanaman_id,
                nama_tanaman,
                deskripsi_tanaman,
            ) = row

            print(f"\nLahan ID       : {lahan_id}")
            print(f"  Petani       : {nama_petani} (ID {petani_id})")
            print(f"  Tanah        : {tanah}")
            print(f"  Ketinggian   : {ketinggian}")
            print(f"  Iklim        : {iklim}")
            print(f"  Tgl Input    : {tanggal_input}")

            if survey_id is not None:
                print(f"  Survey ID    : {survey_id}")
                print(f"  Surveyor     : {nama_surveyor} (ID {surveyor_id})")
                print(f"  Hasil Survey : {hasil_survey}")
                print(f"  Tgl Survey   : {tanggal_survey}")
            else:
                print("  Survey       : (belum ada data survey)")

            if tanaman_id is not None:
                print(f"  Tanaman      : {nama_tanaman} (ID {tanaman_id})")
                print(f"  Deskripsi    : {deskripsi_tanaman}")
            else:
                print("  Tanaman      : (belum ada penanaman)")

    return rows