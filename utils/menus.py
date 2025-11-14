from core.admin_functions import add_user
from core.analysis import add_lahan, input_angka, add_tanaman
from utils.header import header


def menu_admin(conn, user):
    """
    Menu untuk role admin:
    - Tambah user baru (admin/petani/surveyor)
    """
    while True:
        header()
        print(f"\n=== MENU ADMIN (Login sebagai: {user['username']}) ===")
        print("1. Tambah user baru")
        print("0. Logout")

        pilihan = input("Pilih menu: ").strip()

        if pilihan == "1":
            print("\n=== Tambah User Baru ===")
            username = input("Username: ")
            password = input("Password: ")
            print("Pilih role:")
            print("1. admin")
            print("2. petani")
            print("3. surveyor")
            role_pilihan = input("Role (1/2/3): ").strip()

            if role_pilihan == "1":
                role = "admin"
            elif role_pilihan == "2":
                role = "petani"
            elif role_pilihan == "3":
                role = "surveyor"
            else:
                print("Role tidak valid.")
                continue

            try:
                user_id = add_user(conn, username, password, role)
                print(f"✅ User baru dengan ID {user_id} dan role '{role}' berhasil ditambahkan.")
            except Exception as error:
                print(f"Ada error: {error}")
                break

        elif pilihan == "0":
            print("Logout dari admin.")
            break
        else:
            print("Pilihan tidak valid, coba lagi.")


def menu_petani(conn, user):
    """
    Menu untuk role petani:
    - Input tanaman
    - (opsional) Input lahan milik dirinya sendiri
    """
    petani_id = user["user_id"]

    while True:
        header()
        print(f"\n=== MENU PETANI (Login sebagai: {user['username']}) ===")
        print("1. Input tanaman")
        print("2. Input lahan milik saya")
        print("0. Logout")

        pilihan = input("Pilih menu: ").strip()

        if pilihan == "1":
            print("\n=== Input Data Tanaman ===")
            nama_tanaman = input("Nama tanaman: ")
            deskripsi_tanaman = input("Deskripsi tanaman (boleh kosong): ")
            if deskripsi_tanaman.strip() == "":
                deskripsi_tanaman = None

            tanaman_id = add_tanaman(conn, nama_tanaman, deskripsi_tanaman)
            print(f"✅ Tanaman dengan ID {tanaman_id} berhasil ditambahkan.")

        elif pilihan == "2":
            print("\n=== Input Data Lahan ===")
            lokasi = input("Lokasi lahan: ")
            ketinggian = input_angka("Ketinggian (meter): ", float)
            ph = input_angka("pH tanah: ", float)
            tekstur = input("Tekstur tanah: ")
            kandungan_nutrisi = input("Kandungan nutrisi: ")
            suhu = input_angka("Suhu (°C): ", float)
            curah_hujan = input_angka("Curah hujan (mm): ", float)

            lahan_id = add_lahan(
                conn,
                petani_id,
                lokasi,
                ketinggian,
                ph,
                tekstur,
                kandungan_nutrisi,
                suhu,
                curah_hujan
            )
            print(f"✅ Lahan dengan ID {lahan_id} berhasil ditambahkan.")

        elif pilihan == "0":
            print("Logout dari petani.")
            break
        else:
            print("Pilihan tidak valid, coba lagi.")


def menu_surveyor(conn, user):
    """
    Menu untuk role surveyor:
    - Input data lahan hasil survey
    (di sini surveyor harus pilih petani_id yang terkait,
     bisa dikembangkan lagi nanti dengan daftar petani)
    """
    while True:
        header()
        print(f"\n=== MENU SURVEYOR (Login sebagai: {user['username']}) ===")
        print("1. Input data lahan (survey)")
        print("0. Logout")

        pilihan = input("Pilih menu: ").strip()

        if pilihan == "1":
            print("\n=== Input Data Lahan (Survey) ===")
            petani_id = input_angka("Masukkan ID Petani yang disurvey: ", int)
            lokasi = input("Lokasi lahan: ")
            ketinggian = input_angka("Ketinggian (meter): ", float)
            ph = input_angka("pH tanah: ", float)
            tekstur = input("Tekstur tanah: ")
            kandungan_nutrisi = input("Kandungan nutrisi: ")
            suhu = input_angka("Suhu (°C): ", float)
            curah_hujan = input_angka("Curah hujan (mm): ", float)

            lahan_id = add_lahan(
                conn,
                petani_id,
                lokasi,
                ketinggian,
                ph,
                tekstur,
                kandungan_nutrisi,
                suhu,
                curah_hujan
            )
            print(f"✅ Data lahan hasil survey dengan ID {lahan_id} berhasil ditambahkan.")

        elif pilihan == "0":
            print("Logout dari surveyor.")
            break
        else:
            print("Pilihan tidak valid, coba lagi.")
