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
    conn,
    id_user_surveyor: int,
    id_alamat: int | None,
    ketinggian: float,
) -> Optional[int]:
    """
    Tambah data lahan.
    :return: lahan_id atau None.
    """
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO lahan (id_user_surveyor, id_alamat, ketinggian)
            VALUES (%s, %s, %s)
            RETURNING lahan_id;
            """,
            (id_user_surveyor, id_alamat, ketinggian),
        )
        row = cur.fetchone()
        conn.commit()
        return row[0] if row else None


def lihat_lahan_universal(conn, user: dict[str, Any]) -> list[tuple[Any, ...]]:
    """
    user = {"id": user_id, "role": "admin"|"petani"|"surveyor"}
    """
    role = user["role"].lower()
    user_id = user["id"]

    with conn.cursor() as cur:
        if role == "surveyor":
            cur.execute(
                """
                SELECT
                    l.lahan_id,
                    u_s.name      AS nama_surveyor,
                    l.ketinggian,
                    a.nama_jalan,
                    k.nama_kecamatan,
                    kt.nama_kota,
                    p.nama_provinsi
                FROM lahan l
                LEFT JOIN users u_s      ON u_s.user_id = l.id_user_surveyor
                LEFT JOIN alamat a       ON a.alamat_id = l.id_alamat
                LEFT JOIN kecamatan k    ON k.kecamatan_id = a.id_kecamatan
                LEFT JOIN kota kt        ON kt.kota_id = a.id_kota
                LEFT JOIN provinsi p     ON p.provinsi_id = a.id_provinsi
                WHERE l.id_user_surveyor = %s
                ORDER BY l.lahan_id;
                """,
                (user_id,),
            )

        elif role == "petani":
            # asumsi: petani = user yang punya tanaman di lahan tsb
            cur.execute(
                """
                SELECT DISTINCT
                    l.lahan_id,
                    u_s.name      AS nama_surveyor,
                    l.ketinggian,
                    a.nama_jalan,
                    k.nama_kecamatan,
                    kt.nama_kota,
                    p.nama_provinsi
                FROM lahan l
                JOIN survey_data sd   ON sd.id_lahan = l.lahan_id
                JOIN tanaman t        ON t.tanaman_id = sd.id_tanaman
                JOIN users u_p        ON u_p.user_id = t.id_user
                LEFT JOIN users u_s   ON u_s.user_id = l.id_user_surveyor
                LEFT JOIN alamat a    ON a.alamat_id = l.id_alamat
                LEFT JOIN kecamatan k ON k.kecamatan_id = a.id_kecamatan
                LEFT JOIN kota kt     ON kt.kota_id = a.id_kota
                LEFT JOIN provinsi p  ON p.provinsi_id = a.id_provinsi
                WHERE u_p.user_id = %s
                ORDER BY l.lahan_id;
                """,
                (user_id,),
            )

        else:  # admin atau role lain → lihat semua
            cur.execute(
                """
                SELECT
                    l.lahan_id,
                    u_s.name      AS nama_surveyor,
                    l.ketinggian,
                    a.nama_jalan,
                    k.nama_kecamatan,
                    kt.nama_kota,
                    p.nama_provinsi
                FROM lahan l
                LEFT JOIN users u_s   ON u_s.user_id = l.id_user_surveyor
                LEFT JOIN alamat a    ON a.alamat_id = l.id_alamat
                LEFT JOIN kecamatan k ON k.kecamatan_id = a.id_kecamatan
                LEFT JOIN kota kt     ON kt.kota_id = a.id_kota
                LEFT JOIN provinsi p  ON p.provinsi_id = a.id_provinsi
                ORDER BY l.lahan_id;
                """
            )

        rows = cur.fetchall()

    print("\n=== Daftar Lahan ===")
    if not rows:
        print("\nMasih kosong")
    else:
        for (
            lahan_id,
            nama_surveyor,
            ketinggian,
            nama_jalan,
            nama_kecamatan,
            nama_kota,
            nama_provinsi,
        ) in rows:
            print(
                f"- ID: {lahan_id} | Surveyor: {nama_surveyor} | "
                f"Ketinggian: {ketinggian} | Alamat: {nama_jalan}, "
                f"{nama_kecamatan}, {nama_kota}, {nama_provinsi}"
            )

    return rows



def add_tanaman(
    conn,
    id_user: int,
    id_tipe_tanaman: int,
    nama_tanaman: str,
) -> Optional[int]:
    """
    Tambah tanaman ke tabel tanaman (skema baru).
    """
    with conn.cursor() as cur:
        # cek duplikat nama untuk user yang sama (opsional)
        cur.execute(
            """
            SELECT 1
            FROM tanaman
            WHERE LOWER(nama) = LOWER(%s)
              AND id_user = %s
            """,
            (nama_tanaman, id_user),
        )
        if cur.fetchone():
            print(f"Nama tanaman '{nama_tanaman}' sudah ada untuk user ini.")
            return None

        cur.execute(
            """
            INSERT INTO tanaman (id_tipe_tanaman, id_user, nama)
            VALUES (%s, %s, %s)
            RETURNING tanaman_id;
            """,
            (id_tipe_tanaman, id_user, nama_tanaman),
        )
        row = cur.fetchone()
        conn.commit()
        tanaman_id = row[0] if row else None
        if tanaman_id is not None:
            print(
                f"Tanaman '{nama_tanaman}' (ID {tanaman_id}) berhasil disimpan."
            )
        return tanaman_id


def add_survey_data(
    conn,
    id_lahan: int,
    id_user_surveyor: int,
    id_user_admin: int | None,
    id_iklim: int,
    id_tanah: int,
    nama_tanaman: str | None = None,
    id_tanaman: int | None = None,
    status_survey: str = "waiting",
) -> Optional[int]:
    """
    Tambah record ke survey_data.
    """
    tanggal = date.today()

    query = """
        INSERT INTO survey_data (
            nama_tanaman,
            id_user_surveyor,
            id_user_admin,
            id_lahan,
            id_iklim,
            id_tanah,
            status_survey,
            id_tanaman,
            tanggal_survey
        ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
        RETURNING survey_id;
    """

    with conn.cursor() as cur:
        cur.execute(
            query,
            (
                nama_tanaman,
                id_user_surveyor,
                id_user_admin,
                id_lahan,
                id_iklim,
                id_tanah,
                status_survey,
                id_tanaman,
                tanggal,
            ),
        )
        row = cur.fetchone()
        conn.commit()
        return row[0] if row else None


def analysis_tanaman_dengan_lahan(conn) -> list[tuple[Any, ...]]:
    """
    Join lahan + survey_data + tanaman + user (petani & surveyor) + alamat.
    """
    query = """
        SELECT
            l.lahan_id,
            u_surveyor.user_id      AS surveyor_id,
            u_surveyor.name         AS nama_surveyor,

            l.ketinggian,
            a.nama_jalan,
            kc.nama_kecamatan,
            k.nama_kota,
            p.nama_provinsi,

            sd.survey_id,
            sd.status_survey,
            sd.tanggal_survey,

            ik.jenis_cuaca,
            ktan.kondisi_tanah,
            ktan.ph,
            ktan.kandungan_nutrisi,
            ktan.kelembapan,

            t.tanaman_id,
            t.nama                AS nama_tanaman,
            u_petani.user_id      AS petani_id,
            u_petani.name         AS nama_petani
        FROM lahan l
        LEFT JOIN users u_surveyor   ON u_surveyor.user_id = l.id_user_surveyor
        LEFT JOIN alamat a           ON a.alamat_id = l.id_alamat
        LEFT JOIN kecamatan kc       ON kc.kecamatan_id = a.id_kecamatan
        LEFT JOIN kota k             ON k.kota_id = a.id_kota
        LEFT JOIN provinsi p         ON p.provinsi_id = a.id_provinsi

        LEFT JOIN survey_data sd     ON sd.id_lahan = l.lahan_id
        LEFT JOIN iklim ik           ON ik.iklim_id = sd.id_iklim
        LEFT JOIN kondisi_tanah ktan ON ktan.kondisi_tanah_id = sd.id_tanah

        LEFT JOIN tanaman t          ON t.tanaman_id = sd.id_tanaman
        LEFT JOIN users u_petani     ON u_petani.user_id = t.id_user

        ORDER BY l.lahan_id, sd.survey_id, t.tanaman_id;
    """

    with conn.cursor() as cur:
        cur.execute(query)
        rows = cur.fetchall()

    if not rows:
        print("\nBelum ada data analisis lahan + tanaman.")
        return rows

    print("\n=== HASIL ANALISIS LAHAN + TANAMAN ===")
    for row in rows:
        (
            lahan_id,
            surveyor_id,
            nama_surveyor,
            ketinggian,
            nama_jalan,
            nama_kecamatan,
            nama_kota,
            nama_provinsi,
            survey_id,
            status_survey,
            tanggal_survey,
            jenis_cuaca,
            kondisi_tanah,
            ph,
            kandungan_nutrisi,
            kelembapan,
            tanaman_id,
            nama_tanaman,
            petani_id,
            nama_petani,
        ) = row

        print(f"\nLahan ID   : {lahan_id}")
        print(f"  Surveyor : {nama_surveyor} (ID {surveyor_id})")
        print(f"  Ketinggian : {ketinggian}")
        print(
            f"  Alamat   : {nama_jalan}, {nama_kecamatan}, "
            f"{nama_kota}, {nama_provinsi}"
        )

        if survey_id is not None:
            print(f"  Survey ID    : {survey_id}")
            print(f"  Status       : {status_survey}")
            print(f"  Tgl Survey   : {tanggal_survey}")
            print(f"  Iklim        : {jenis_cuaca}")
            print(
                f"  Tanah        : {kondisi_tanah} | pH={ph} | "
                f"Nutrisi={kandungan_nutrisi} | Kelembapan={kelembapan}"
            )
        else:
            print("  Survey       : (belum ada)")

        if tanaman_id is not None:
            print(
                f"  Tanaman      : {nama_tanaman} (ID {tanaman_id}) "
                f"oleh {nama_petani} (ID {petani_id})"
            )
        else:
            print("  Tanaman      : (belum ada)")
    return rows
