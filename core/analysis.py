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
        conn, petani_id: int, lokasi: str, ketinggian: float, ph: float, tekstur: str,
        kandungan_nutrisi: str, suhu: float, curah_hujan: float
) -> tuple[str] | None:
    """
    Inputan lahan
    :param conn:
    :param petani_id:
    :param lokasi:
    :param ketinggian:
    :param ph:
    :param tekstur:
    :param kandungan_nutrisi:
    :param suhu:
    :param curah_hujan:
    :return tuple[str] | None:
    """
    tanggal = date.today()

    query = (f"INSERT INTO lahan WITH VALUES ({petani_id}, {lokasi}, {ketinggian}, {ph}, {tekstur}, "
             f"{kandungan_nutrisi}, {suhu}, {curah_hujan}, {tanggal}) RETURNING *;")
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

    query = f"INSERT INTO tanaman WITH VALUES ({nama_tanaman}, {deskripsi}) RETURNING *;"
    cursor.execute(query)
    result = cursor.fetchone()
    conn.commit()
    cursor.close()
    print(f"nama tanaman {nama_tanaman} dengan deskripsi {deskripsi} sudah masuk")
    return result

