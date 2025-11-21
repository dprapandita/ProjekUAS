from datetime import date
from typing import Optional, Any

from utils.address import get_or_create_alamat_master


def add_lahan(
    conn,
    id_user_petani: int | None,
    id_user_surveyor: int | None,
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
            INSERT INTO lahan (id_user_petani, id_user_surveyor, id_alamat, ketinggian)
            VALUES (%s, %s, %s, %s)
            RETURNING lahan_id;
            """,
            (id_user_petani, id_user_surveyor, id_alamat, ketinggian),
        )
        row = cur.fetchone()
        conn.commit()
        return row[0] if row else None


def lihat_lahan_universal(conn, user: dict[str, Any]) -> list[tuple[Any, ...]]:
    role = user["role"].lower()
    user_id = user["id"]

    with conn.cursor() as cur:
        if role == "surveyor":
            cur.execute(
                """
                SELECT
                    l.lahan_id,
                    u_p.name        AS nama_petani,
                    u_s.user_id     AS surveyor_id,
                    u_s.name        AS nama_surveyor,
                    l.ketinggian,
                    a.nama_jalan,
                    kc.nama_kecamatan,
                    kt.nama_kota,
                    p.nama_provinsi
                FROM lahan l
                LEFT JOIN users u_p       ON u_p.user_id      = l.id_user_petani
                LEFT JOIN users u_s       ON u_s.user_id      = l.id_user_surveyor
                LEFT JOIN alamat a        ON a.alamat_id      = l.id_alamat
                LEFT JOIN kecamatan kc    ON kc.kecamatan_id  = a.id_kecamatan
                LEFT JOIN kota kt         ON kt.kota_id       = a.id_kota
                LEFT JOIN provinsi p      ON p.provinsi_id    = a.id_provinsi
                ORDER BY l.lahan_id;
                """
            )
        elif role == "petani":
            cur.execute(
                """
                SELECT
                    l.lahan_id,
                    u_p.name        AS nama_petani,
                    u_s.user_id     AS surveyor_id,
                    u_s.name        AS nama_surveyor,
                    l.ketinggian,
                    a.nama_jalan,
                    kc.nama_kecamatan,
                    kt.nama_kota,
                    p.nama_provinsi
                FROM lahan l
                LEFT JOIN users u_p       ON u_p.user_id      = l.id_user_petani
                LEFT JOIN users u_s       ON u_s.user_id      = l.id_user_surveyor
                LEFT JOIN alamat a        ON a.alamat_id      = l.id_alamat
                LEFT JOIN kecamatan kc    ON kc.kecamatan_id  = a.id_kecamatan
                LEFT JOIN kota kt         ON kt.kota_id       = a.id_kota
                LEFT JOIN provinsi p      ON p.provinsi_id    = a.id_provinsi
                WHERE l.id_user_petani = %s
                ORDER BY l.lahan_id;
                """,
                (user_id,),
            )
        else:  # admin
            cur.execute(
                """
                SELECT
                    l.lahan_id,
                    u_p.name        AS nama_petani,
                    u_s.user_id     AS surveyor_id,
                    u_s.name        AS nama_surveyor,
                    l.ketinggian,
                    a.nama_jalan,
                    kc.nama_kecamatan,
                    kt.nama_kota,
                    p.nama_provinsi
                FROM lahan l
                LEFT JOIN users u_p       ON u_p.user_id      = l.id_user_petani
                LEFT JOIN users u_s       ON u_s.user_id      = l.id_user_surveyor
                LEFT JOIN alamat a        ON a.alamat_id      = l.id_alamat
                LEFT JOIN kecamatan kc    ON kc.kecamatan_id  = a.id_kecamatan
                LEFT JOIN kota kt         ON kt.kota_id       = a.id_kota
                LEFT JOIN provinsi p      ON p.provinsi_id    = a.id_provinsi
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
            nama_petani,
            surveyor_id,
            nama_surveyor,
            ketinggian,
            nama_jalan,
            nama_kecamatan,
            nama_kota,
            nama_provinsi,
        ) in rows:
            if surveyor_id is None:
                status = "BELUM DIAMBIL"
            else:
                status = f"SUDAH DIAMBIL oleh {nama_surveyor}"

            print(
                f"- ID: {lahan_id} | Petani: {nama_petani} | "
                f"Ketinggian: {ketinggian} | Alamat: {nama_jalan}, "
                f"{nama_kecamatan}, {nama_kota}, {nama_provinsi} | Status: {status}"
            )

    return rows


def add_tanaman(
    conn,
    id_tipe_tanaman: int,
    nama_tanaman: str,
) -> Optional[int]:
    """
    Tambah tanaman ke tabel tanaman (schema: id_tipe_tanaman, nama).
    """
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT 1
            FROM tanaman
            WHERE LOWER(nama) = LOWER(%s)
              AND id_tipe_tanaman = %s
            """,
            (nama_tanaman, id_tipe_tanaman),
        )
        if cur.fetchone():
            print(
                f"Nama tanaman '{nama_tanaman}' sudah ada untuk tipe {id_tipe_tanaman}."
            )
            return None

        cur.execute(
            """
            INSERT INTO tanaman (id_tipe_tanaman, nama)
            VALUES (%s, %s)
            RETURNING tanaman_id;
            """,
            (id_tipe_tanaman, nama_tanaman),
        )
        row = cur.fetchone()
        conn.commit()

        tanaman_id = row[0] if row else None
        if tanaman_id is not None:
            print(f"Tanaman '{nama_tanaman}' (ID {tanaman_id}) berhasil disimpan.")
        return tanaman_id


def add_survey_data(
    conn,
    id_lahan: int,
    id_user_surveyor: int,
    id_user_admin: Optional[int],
    id_iklim: int,
    id_tanah: int,
    nama_tanaman: Optional[str] = None,
    id_tanaman: Optional[int] = None,
    status_survey: str = "waiting",
) -> Optional[int]:
    """
    Tambah record ke survey_data sesuai definisi tabel:
    nama_tanaman, id_user_surveyor, id_user_admin,
    id_lahan, id_iklim, id_tanah, status_survey, id_tanaman, tanggal_survey.
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


def claim_lahan_for_surveyor(
    conn,
    lahan_id: int,
    surveyor_id: int,
) -> bool:
    """
    Coba klaim lahan untuk surveyor.
    Hanya berhasil kalau id_user_surveyor masih NULL.
    Return True kalau berhasil, False kalau gagal (sudah diambil orang lain).
    """
    with conn.cursor() as cur:
        cur.execute(
            """
            UPDATE lahan
            SET id_user_surveyor = %s
            WHERE lahan_id = %s
              AND id_user_surveyor IS NULL;
            """,
            (surveyor_id, lahan_id),
        )
        if cur.rowcount == 0:
            conn.rollback()
            return False

        conn.commit()
        return True


def buat_alamat(conn) -> int | None:
    nama_jalan = input("Nama jalan: ").strip()
    if not nama_jalan:
        print("Nama jalan wajib diisi.")
        return None

    nama_provinsi = input("Nama provinsi (boleh kosong): ").strip()
    nama_kota = input("Nama kota (boleh kosong): ").strip()
    nama_kecamatan = input("Nama kecamatan (boleh kosong): ").strip()

    id_provinsi = get_or_create_alamat_master(conn, "provinsi", nama_provinsi) if nama_provinsi else None
    id_kota = get_or_create_alamat_master(conn, "kota", nama_kota) if nama_kota else None
    id_kecamatan = get_or_create_alamat_master(conn, "kecamatan", nama_kecamatan) if nama_kecamatan else None

    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO alamat (nama_jalan, id_kota, id_kecamatan, id_provinsi)
            VALUES (%s, %s, %s, %s)
            RETURNING alamat_id;
            """,
            (nama_jalan,
             int(id_kota) if id_kota else None,
             int(id_kecamatan) if id_kecamatan else None,
             int(id_provinsi) if id_provinsi else None),
        )
        row = cur.fetchone()
        conn.commit()
        return row[0] if row else None


def analysis_tanaman_dengan_lahan(conn) -> list[tuple[Any, ...]]:
    """
    Join lahan + survey_data + tanaman + user (petani & surveyor) + alamat,
    disesuaikan dengan schema terbaru (tanaman tidak punya id_user).
    """
    query = """
        SELECT
            l.lahan_id,

            u_surveyor.user_id   AS surveyor_id,
            u_surveyor.name      AS nama_surveyor,

            u_petani.user_id     AS petani_id,
            u_petani.name        AS nama_petani,

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
            t.nama             AS nama_tanaman
        FROM lahan l
        LEFT JOIN users u_petani     ON u_petani.user_id      = l.id_user_petani
        LEFT JOIN users u_surveyor   ON u_surveyor.user_id    = l.id_user_surveyor

        LEFT JOIN alamat a           ON a.alamat_id           = l.id_alamat
        LEFT JOIN kecamatan kc       ON kc.kecamatan_id       = a.id_kecamatan
        LEFT JOIN kota k             ON k.kota_id             = a.id_kota
        LEFT JOIN provinsi p         ON p.provinsi_id         = a.id_provinsi

        LEFT JOIN survey_data sd     ON sd.id_lahan           = l.lahan_id
        LEFT JOIN iklim ik           ON ik.iklim_id           = sd.id_iklim
        LEFT JOIN kondisi_tanah ktan ON ktan.kondisi_tanah_id = sd.id_tanah

        LEFT JOIN tanaman t          ON t.tanaman_id          = sd.id_tanaman

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
            petani_id,
            nama_petani,
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
        ) = row

        print(f"\nLahan ID   : {lahan_id}")
        print(f"  Petani   : {nama_petani} (ID {petani_id})")
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
                f"  Tanaman      : {nama_tanaman} (ID {tanaman_id})"
            )
        else:
            print("  Tanaman      : (belum ada)")

    return rows


def lihat_hasil_survey_petani(conn, user: dict[str, Any]) -> list[tuple[Any, ...]]:
    """
    Tampilkan hasil analisis (survey) untuk semua lahan milik petani yang login.
    Fokus ke data yang DISURVEY oleh surveyor (tabel survey_data).
    """
    user_id = user["id"]

    query = """
        SELECT
            l.lahan_id,
            l.ketinggian,

            -- pemilik lahan (petani)
            u_petani.user_id      AS petani_id,
            u_petani.name         AS nama_petani,

            -- surveyor yang menganalisis
            u_surveyor.user_id    AS surveyor_id,
            u_surveyor.name       AS nama_surveyor,

            -- alamat lahan
            a.nama_jalan,
            kc.nama_kecamatan,
            k.nama_kota,
            p.nama_provinsi,

            -- data survey
            sd.survey_id,
            sd.tanggal_survey,
            sd.status_survey,

            -- iklim & tanah
            ik.jenis_cuaca,
            ktan.kondisi_tanah,
            ktan.ph,
            ktan.kandungan_nutrisi,
            ktan.kelembapan,

            -- tanaman (kalau surveyor pilih dari master)
            t.tanaman_id,
            t.nama              AS nama_tanaman_master
            
        FROM lahan l
        JOIN users u_petani          ON u_petani.user_id      = l.id_user_petani
        JOIN survey_data sd          ON sd.id_lahan           = l.lahan_id
        LEFT JOIN users u_surveyor   ON u_surveyor.user_id    = sd.id_user_surveyor

        LEFT JOIN alamat a           ON a.alamat_id           = l.id_alamat
        LEFT JOIN kecamatan kc       ON kc.kecamatan_id       = a.id_kecamatan
        LEFT JOIN kota k             ON k.kota_id             = a.id_kota
        LEFT JOIN provinsi p         ON p.provinsi_id         = a.id_provinsi

        LEFT JOIN iklim ik           ON ik.iklim_id           = sd.id_iklim
        LEFT JOIN kondisi_tanah ktan ON ktan.kondisi_tanah_id = sd.id_tanah
        LEFT JOIN tanaman t          ON t.tanaman_id          = sd.id_tanaman

        WHERE l.id_user_petani = %s
        ORDER BY l.lahan_id, sd.tanggal_survey DESC, sd.survey_id;
    """

    with conn.cursor() as cur:
        cur.execute(query, (user_id,))
        rows = cur.fetchall()

    if not rows:
        print("\nBelum ada hasil survey untuk lahan kamu.")
        return rows

    print("\n=== HASIL ANALISIS (SURVEY) LAHAN SAYA ===")
    current_lahan = None
    for row in rows:
        (
            lahan_id,
            ketinggian,
            petani_id,
            nama_petani,
            surveyor_id,
            nama_surveyor,
            nama_jalan,
            nama_kecamatan,
            nama_kota,
            nama_provinsi,
            survey_id,
            tanggal_survey,
            status_survey,
            jenis_cuaca,
            kondisi_tanah,
            ph,
            kandungan_nutrisi,
            kelembapan,
            tanaman_id,
            nama_tanaman_master
        ) = row

        # biar per-lahan ngelompok, kasih header kalau ganti lahan_id
        if current_lahan != lahan_id:
            current_lahan = lahan_id
            print("\n----------------------------------------")
            print(f"Lahan ID   : {lahan_id}")
            print(f"  Pemilik  : {nama_petani} (ID {petani_id})")
            print(f"  Ketinggian : {ketinggian}")
            print(
                f"  Alamat   : {nama_jalan}, {nama_kecamatan}, "
                f"{nama_kota}, {nama_provinsi}"
            )
            print("  Survey:")

        # nama tanaman: ambil dari master kalau ada, kalau nggak, pakai yang manual
        if nama_tanaman_master:
            rekom_tanaman = f"{nama_tanaman_master} (ID {tanaman_id})"
        else:
            rekom_tanaman = "-"

        print(f"    • Survey ID    : {survey_id}")
        print(f"      Oleh         : {nama_surveyor} (ID {surveyor_id})")
        print(f"      Tgl Survey   : {tanggal_survey}")
        print(f"      Status       : {status_survey}")
        print(f"      Iklim        : {jenis_cuaca}")
        print(
            f"      Tanah        : {kondisi_tanah} | pH={ph} | "
            f"Nutrisi={kandungan_nutrisi} | Kelembapan={kelembapan}"
        )
        print(f"      Rekom Tanaman: {rekom_tanaman}")

    return rows


def get_all_tipe_tanaman(conn) -> list[tuple[int, str]]:
    """
    Ambil semua baris dari tabel tipe_tanaman:
    (tipe_tanaman_id, jenis_tanaman)
    """
    with conn.cursor() as cur:
        cur.execute(
            "SELECT tipe_tanaman_id, jenis_tanaman "
            "FROM tipe_tanaman "
            "ORDER BY tipe_tanaman_id;"
        )
        return cur.fetchall()


def get_tanaman_by_tipe(conn, tipe_id: int) -> list[tuple[int, str]]:
    """
    Ambil semua tanaman berdasarkan id_tipe_tanaman.
    """
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT tanaman_id, nama
            FROM tanaman
            WHERE id_tipe_tanaman = %s
            ORDER BY nama;
            """,
            (tipe_id,),
        )
        return cur.fetchall()


def get_all_iklim(conn) -> list[tuple[int, str]]:
    """
    Ambil semua data dari tabel iklim:
    (iklim_id, jenis_cuaca)
    """
    with conn.cursor() as cur:
        cur.execute(
            "SELECT iklim_id, jenis_cuaca "
            "FROM iklim "
            "ORDER BY iklim_id;"
        )
        return cur.fetchall()


def get_all_kondisi_tanah(conn) -> list[tuple[Any, ...]]:
    """
    Ambil semua data dari tabel kondisi_tanah:
    (kondisi_tanah_id, kondisi_tanah, ph, kandungan_nutrisi, kelembapan)
    """
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT kondisi_tanah_id, kondisi_tanah, ph, kandungan_nutrisi, kelembapan
            FROM kondisi_tanah
            ORDER BY kondisi_tanah_id;
            """
        )
        return cur.fetchall()