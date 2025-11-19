from core.admin_functions import read_all_users, delete_user, lihat_data_lahan
from core.analysis import add_lahan, input_angka, add_tanaman, add_survey_data, lihat_lahan_universal
from utils.header import header, clear_terminal


def enter_break():
    input("\nTekan Enter untuk lanjut...")  

def menu_admin(conn, user):
    """
    Menu untuk role admin:
    - Hapus users
    - Lihat users
    - Lihat data lahan
    """

    while True:
        clear_terminal()
        header()
        print(f"\n=== MENU ADMIN (Login sebagai: {user['username']}) ===")
        print("1. Hapus user")
        print("2. Lihat user")
        print("3. Lihat data lahan")
        print("0. Logout")

        pilihan = input("Pilih menu: ").strip()

        if pilihan == "1":
            print("\n=== Hapus user ===")
            username = input("Username: ")
            role = str(input("Role: ")).strip().lower()

            try:
                user_id = delete_user(conn, username, role)
                if user_id is None:
                    print(f"⚠️ User '{username}' dengan role '{role}' tidak ditemukan atau tidak dihapus.")
                else:
                    print(f"✅ User dengan ID {user_id} dari {role} berhasil dihapus")
            except Exception as error:
                print(f"Ada error: {error}")
            enter_break()

        elif pilihan == "2":
            users = read_all_users(conn)
            print("\n=== Daftar user ===")
            petani_list = users["petani"]
            surveyor_list = users["surveyor"]

            print(f"\nPetani ({len(petani_list)}):")
            if not petani_list:
                print("  (belum ada petani)")
            else:
                for petani_id, username in petani_list:
                    print(f"  - ID: {petani_id} | Username: {username}")

            print(f"\nSurveyor ({len(surveyor_list)}):")
            if not surveyor_list:
                print("  (belum ada surveyor)")
            else:
                for surveyor_id, username in surveyor_list:
                    print(f"  - ID: {surveyor_id} | Username: {username}")
            enter_break()

        elif pilihan == "3":
            data = lihat_data_lahan(conn)

            print("\n=== Data Petani ===")
            for petani_id, username in data["petani"]:
                print(f"- ID: {petani_id} | Username: {username}")

            print("\n=== Data Lahan ===")
            for lahan_id, petani_id, tanah, ketinggian, iklim, tanggal in data["lahan"]:
                print(
                    f"- Lahan {lahan_id} | Petani {petani_id} | Iklim: {iklim} | Tanah: {tanah} | Ketinggian: {ketinggian} | Tgl: {tanggal}")

            print("\n=== Data Survey ===")
            for survey_id, lahan_id, surveyor_id, hasil, tanggal in data["survey_data"]:
                print(
                    f"- Survey {survey_id} | Lahan {lahan_id} | Surveyor {surveyor_id} | Hasil: {hasil} | Tgl: {tanggal}")
            enter_break()

        elif pilihan == "0":
            print("Logout dari admin.")
            break
        else:
            print("Pilihan tidak valid, coba lagi.")
            enter_break()


def menu_petani(conn, user):
    """
    Menu untuk role petani:
    - Input lahan milik petani
    """
    petani_id = user["id"]

    while True:
        clear_terminal()
        header()
        print(f"\n=== MENU PETANI (Login sebagai: {user['username']}) ===")
        print("1. Input lahan milik saya")
        print("2. Lihat lahan saya")
        print("3. Lihat hasil analisis di lahan saya")
        print("0. Logout")

        pilihan = input("Pilih menu: ").strip()

        if pilihan == "1":
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
            if lahan_id is not None:
                print(f"✅ Lahan dengan ID {lahan_id} berhasil ditambahkan.")
            else:
                print("⚠️ Gagal menambahkan lahan.")
            enter_break()

        elif pilihan == "2":
            lihat_lahan_universal(conn, user)

        elif pilihan == "0":
            print("Logout dari petani.")
            break
        else:
            print("Pilihan tidak valid, coba lagi.")
            enter_break()


def menu_surveyor(conn, user):
    """
    Menu untuk role surveyor:
    - Input data lahan hasil survey
    (di sini surveyor harus pilih petani_id yang terkait,
     bisa dikembangkan lagi nanti dengan daftar petani)
    """
    surveyor_id = user["id"]
    while True:
        clear_terminal()
        header()
        print(f"\n=== MENU SURVEYOR (Login sebagai: {user['username']}) ===")
        print("1. Survey lahan yang sudah ada")
        print('2. Input tanaman')
        print("0. Logout")

        pilihan = input("Pilih menu: ").strip()

        if pilihan == "1":
            lihat_lahan_universal(conn, user)
            print("\n=== Input survey ===")
            lahan_id = int(input("ID lahan yang disurvey: "))
            hasil_survey = input("Hasil survey (deskripsi): ")
            survey_id = add_survey_data(conn, lahan_id, surveyor_id, hasil_survey)
            print(f"✅ Survey baru dengan ID {survey_id} berhasil ditambahkan untuk lahan {lahan_id}.")
            enter_break()

        elif pilihan == "2":
            print("\n=== Input tanaman baru ===")
            nama_tanaman = str(input("Nama tanaman: ")).strip()
            deskripsi = str(input("Deskripsi tanaman (boleh kosong): ")).strip()

            tanaman_id = add_tanaman(conn, nama_tanaman, deskripsi)
            if tanaman_id is None:
                print("⚠️ Tanaman sudah ada atau gagal ditambahkan.")
            else:
                print(f"✅ Tanaman berhasil ditambah dengan ID {tanaman_id}")
            enter_break()

        elif pilihan == "0":
            print("Logout dari surveyor.")
            break
        else:
            print("Pilihan tidak valid, coba lagi.")
            enter_break()
