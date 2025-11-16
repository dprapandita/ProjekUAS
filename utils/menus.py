from core.admin_functions import add_user
from core.analysis import add_lahan, input_angka, add_tanaman, add_survey_data
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
            ketinggian = input_angka("Ketinggian (meter): ", float)
            iklim = str(input("Iklim: "))
            tekstur = input("Tekstur tanah: ")

            lahan_id = add_lahan(
                conn,
                petani_id,
                ketinggian,
                tekstur,
                iklim
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
    surveyor_id = user["id"]
    while True:
        header()
        print(f"\n=== MENU SURVEYOR (Login sebagai: {user['username']}) ===")
        print("1. Survey lahan yang sudah ada")
        print('2. Input tanaman')
        print("0. Logout")

        pilihan = input("Pilih menu: ").strip()

        if pilihan == "1":
            print("\n=== Input survey ===")
            lahan_id = int(input("ID lahan yang disurvey: "))
            hasil_survey = input("Hasil survey (deskripsi): ")
            survey_id = add_survey_data(conn, lahan_id, surveyor_id, hasil_survey)
            print(f"✅ Survey baru dengan ID {survey_id} berhasil ditambahkan untuk lahan {lahan_id}.")

        elif pilihan == "2":
            print("\n=== Input tanaman baru ===")
            nama_tanaman = str(input("Nama tanaman: ")).strip()
            deskripsi = str(input("Deskripsi tanaman (boleh kosong): ")).strip()

            tanaman_id = add_tanaman(conn, nama_tanaman, deskripsi)
            print(f"Tanaman berhasil ditambah {tanaman_id}")

        elif pilihan == "0":
            print("Logout dari surveyor.")
            break
        else:
            print("Pilihan tidak valid, coba lagi.")
