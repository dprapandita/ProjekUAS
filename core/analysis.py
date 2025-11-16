from datetime import date

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
        except ValueError and AttributeError:
            print("Input harus angka, coba lagi.\n")

def add_lahan(
        conn, petani_id: int, ketinggian: float, tanah: str, iklim: str
) -> tuple[str] | None:
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

    query = (f"INSERT INTO lahan(petani_id, ketinggian, tanah, iklim, tanggal_input) "
             f"VALUES ('{petani_id}', '{ketinggian}', '{tanah}', '{iklim}', '{tanggal}') RETURNING *;")
    cursor = conn.cursor()
    cursor.execute(query)
    lahan_id = cursor.fetchone()[0]
    conn.commit()
    cursor.close()
    return lahan_id

def add_tanaman(conn, nama_tanaman, deskripsi) -> tuple[str, str] | None:
    """
    Inputan tanaman
    :param conn:
    :param nama_tanaman:
    :param deskripsi:
    :return tuple[str, str] | None:
    """
    cursor = conn.cursor()
    check_query = f"SELECT nama FROM tanaman WHERE nama LIKE '{nama_tanaman}'"
    cursor.execute(check_query)
    if cursor.fetchone():
        print(f"nama tanaman {nama_tanaman} sudah ada")
        return None

    query = f"INSERT INTO tanaman VALUES ('{nama_tanaman}', '{deskripsi}') RETURNING *;"
    cursor.execute(query)
    result = cursor.fetchone()
    conn.commit()
    cursor.close()
    print(f"nama tanaman {nama_tanaman} dengan deskripsi {deskripsi} sudah masuk")
    return result


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