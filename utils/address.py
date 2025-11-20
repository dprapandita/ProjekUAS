ALAMAT_MASTER_CONFIG = {
    "provinsi":  ("provinsi",  "provinsi_id",  "nama_provinsi"),
    "kota":      ("kota",      "kota_id",      "nama_kota"),
    "kecamatan": ("kecamatan", "kecamatan_id", "nama_kecamatan"),
}


def add_alamat( conn, nama_jalan: str, id_kota: int | None, id_kecamatan: int | None, id_provinsi: int | None, ) -> int | None:
    """ Insert ke tabel alamat, balikin alamat_id. """
    with conn.cursor() as cur:
        cur.execute( """ 
                    INSERT INTO alamat (nama_jalan, id_kota, id_kecamatan, id_provinsi)
                    VALUES (%s, %s, %s, %s) RETURNING alamat_id; """,
                     (nama_jalan, id_kota, id_kecamatan, id_provinsi), )
        row = cur.fetchone()
        conn.commit()
        return row[0] if row else None


def pilih_alamat_baru(conn) -> int | None:
    """
    Interaktif: user pilih provinsi, kota, kecamatan, lalu isi nama_jalan.
    Return alamat_id (atau None kalau gagal / dibatalkan).
    """
    print("\n=== Ubah / Tambah Alamat ===")

    # 1. Pilih provinsi
    prov_list = get_all_master(conn, "provinsi", "provinsi_id", "nama_provinsi")
    if not prov_list:
        print("Belum ada data provinsi.")
        return None

    print("\nDaftar Provinsi:")
    for pid, nama in prov_list:
        print(f"  {pid}. {nama}")

    prov_raw = input("Pilih ID provinsi (kosongkan kalau tidak tahu): ").strip()
    id_prov = int(prov_raw) if prov_raw else None

    # 2. Pilih kota
    kota_list = get_all_master(conn, "kota", "kota_id", "nama_kota")
    if not kota_list:
        print("Belum ada data kota.")
        return None

    print("\nDaftar Kota:")
    for kid, nama in kota_list:
        print(f"  {kid}. {nama}")

    kota_raw = input("Pilih ID kota (kosongkan kalau tidak tahu): ").strip()
    id_kota = int(kota_raw) if kota_raw else None

    # 3. Pilih kecamatan
    kec_list = get_all_master(conn, "kecamatan", "kecamatan_id", "nama_kecamatan")
    if not kec_list:
        print("Belum ada data kecamatan.")
        return None

    print("\nDaftar Kecamatan:")
    for kid, nama in kec_list:
        print(f"  {kid}. {nama}")

    kec_raw = input("Pilih ID kecamatan (kosongkan kalau tidak tahu): ").strip()
    id_kec = int(kec_raw) if kec_raw else None

    # 4. Nama jalan
    nama_jalan = input("Nama jalan (wajib): ").strip()
    if not nama_jalan:
        print("Nama jalan tidak boleh kosong.")
        return None

    alamat_id = add_alamat(conn, nama_jalan, id_kota, id_kec, id_prov)
    if alamat_id is None:
        print("Gagal menyimpan alamat.")
        return None

    print(f"Alamat baru tersimpan dengan ID {alamat_id}.")
    return alamat_id


def pilih_master_alamat(
    conn,
    table: str,
    id_col: str,
    nama_col: str,
    label: str,
) -> int | None:
    with conn.cursor() as cur:
        cur.execute(
            f"SELECT {id_col}, {nama_col} FROM {table} ORDER BY {nama_col};"
        )
        rows = cur.fetchall()

    if not rows:
        print(f"Belum ada data {label}.")
        return None

    print(f"\n=== Daftar {label.capitalize()} ===")
    for rid, nama in rows:
        print(f"{rid}. {nama}")

    pilih = input(f"Pilih ID {label} (kosong = skip): ").strip()
    if not pilih:
        return None

    try:
        pilih_id = int(pilih)
    except ValueError:
        print("Input harus angka.")
        return None

    valid_ids = {r[0] for r in rows}
    if pilih_id not in valid_ids:
        print(f"ID {label} tidak valid.")
        return None

    return pilih_id


def pilih_master(conn, jenis: str) -> int | None:
    jenis = jenis.lower()
    if jenis not in ALAMAT_MASTER_CONFIG:
        print(f"Jenis '{jenis}' tidak dikenal (harusnya: provinsi/kota/kecamatan).")
        return None

    table, id_col, nama_col = ALAMAT_MASTER_CONFIG[jenis]
    return pilih_master_alamat(conn, table, id_col, nama_col, jenis)


def get_or_create_master(
    conn,
    table: str,
    id_col: str,
    nama_col: str,
    nama: str,
) -> int | None:
    nama = nama.strip()
    if not nama:
        return None

    with conn.cursor() as cur:
        # cek ada atau belum
        cur.execute(
            f"SELECT {id_col} FROM {table} WHERE LOWER({nama_col}) = LOWER(%s)",
            (nama,),
        )
        row = cur.fetchone()
        if row:
            return row[0]

        # belum ada → insert
        cur.execute(
            f"INSERT INTO {table} ({nama_col}) VALUES (%s) RETURNING {id_col};",
            (nama,),
        )
        row = cur.fetchone()
        conn.commit()
        return row[0] if row else None

def get_or_create_alamat_master(conn, jenis: str, nama: str) -> int | None:
    jenis = jenis.lower()
    if jenis not in ALAMAT_MASTER_CONFIG:
        print(f"Jenis '{jenis}' tidak dikenal.")
        return None

    table, id_col, nama_col = ALAMAT_MASTER_CONFIG[jenis]
    return get_or_create_master(conn, table, id_col, nama_col, nama)

def get_all_master(
    conn,
    table: str,
    id_col: str,
    nama_col: str,
) -> list[tuple[int, str]]:
    """
    Ambil semua data dari tabel master (provinsi/kota/kecamatan, dll)
    dalam bentuk (id, nama) terurut.
    """
    with conn.cursor() as cur:
        cur.execute(
            f"""
            SELECT {id_col}, {nama_col}
            FROM {table}
            ORDER BY {nama_col};
            """
        )
        return cur.fetchall()


def get_all_alamat_master(conn, jenis: str) -> list[tuple[int, str]]:
    jenis = jenis.lower()
    if jenis not in ALAMAT_MASTER_CONFIG:
        print(f"Jenis '{jenis}' tidak dikenal (harusnya: provinsi/kota/kecamatan).")
        return []

    table, id_col, nama_col = ALAMAT_MASTER_CONFIG[jenis]
    return get_all_master(conn, table, id_col, nama_col)

