from core.admin_functions import read_all_users, delete_user, lihat_data_lahan, get_user_by_id, update_user_profile
from core.analysis import add_lahan, add_tanaman, add_survey_data, lihat_lahan_universal, get_all_iklim, \
    get_all_kondisi_tanah, get_all_tipe_tanaman, get_tanaman_by_tipe, lihat_hasil_survey_petani, buat_alamat, \
    claim_lahan_for_surveyor
from utils.address import pilih_alamat_baru
from utils.header import header, clear_terminal
from utils.dekorasi import display, input_optional


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
            all_users = read_all_users(conn)
            print("\n=== Daftar user ===")
            petani_list = all_users.get("petani", [])
            surveyor_list = all_users.get("surveyor", [])

            print(f"\nPetani ({len(petani_list)}):")
            if not petani_list:
                print("  (belum ada petani)")
            else:
                for user_id, name, username in petani_list:
                    print(f"  - ID: {user_id} | Nama: {name} | Username: {username}")

            print(f"\nSurveyor ({len(surveyor_list)}):")
            if not surveyor_list:
                print("  (belum ada surveyor)")
            else:
                for user_id, name, username in surveyor_list:
                    print(f"  - ID: {user_id} | Nama: {name} | Username: {username}")

            enter_break()

        elif pilihan == "3":
            data = lihat_data_lahan(conn)
            petani_list = data.get("petani", [])
            data_lahan = data.get("lahan", [])
            data_survey = data.get("survey_data", [])

            print("\n=== Data Petani ===")
            for user_id, name, username, email, no_telp in petani_list:
                print(
                    f"  - ID: {user_id} | Nama: {name} | Username: {username} | "
                    f"Email: {email} | No Telp: {no_telp}"
                )

            print("\n=== Data Lahan ===")
            for lahan_id, petani_id, tanah, ketinggian, iklim, tanggal in data_lahan:
                print(
                    f"- Lahan {lahan_id} | Petani {petani_id} | Iklim: {iklim} | Tanah: {tanah} | Ketinggian: {ketinggian} | Tgl: {tanggal}")

            print("\n=== Data Survey ===")
            for survey_id, lahan_id, surveyor_id, hasil, tanggal in data_survey:
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
        print("4. Upate profile saya")
        print("0. Logout")

        pilihan = input("Pilih menu: ").strip()

        if pilihan == "1":
            print("\n=== Input Data Lahan Milik Saya ===")
            try:
                ketinggian = float(input("Ketinggian (meter): ").strip())
            except ValueError:
                print("Ketinggian harus angka.")
                enter_break()
                continue

            mode = input("1. Pilih alamat yang sudah ada\n2. Buat alamat baru\nPilih: ").strip()

            id_alamat = None
            if mode == "1":
                id_alamat = pilih_alamat_baru(conn)
            elif mode == "2":
                id_alamat = buat_alamat(conn)
            else:
                print("Pilihan mode alamat tidak valid.")
                enter_break()
                continue

            if id_alamat is None:
                print("Alamat nya masih kosong")
                enter_break()
                continue

            lahan_id = add_lahan(
                conn,
                id_user_petani=petani_id,
                id_user_surveyor=None,
                id_alamat=id_alamat,
                ketinggian=ketinggian,
            )
            if lahan_id is not None:
                print(f"✅ Lahan dengan ID {lahan_id} berhasil ditambahkan.")
            else:
                print("⚠️ Gagal menambahkan lahan.")
            enter_break()

        elif pilihan == "2":
            lihat_lahan_universal(conn, user)
            enter_break()

        elif pilihan == "3":
            lihat_hasil_survey_petani(conn, user)
            enter_break()

        elif pilihan == "4":
            menu_update_profile(conn, user)
            enter_break()

        elif pilihan == "0":
            print("Logout dari petani.")
            break
        else:
            print("Pilihan tidak valid, coba lagi.")
            enter_break()


def menu_surveyor(conn, user):
    """
    Menu untuk role surveyor:
    1. Survey lahan yang sudah ada (mengisi survey_data lengkap)
    2. Input tanaman (mengisi tabel tipe_tanaman + tanaman sesuai schema)
    """
    surveyor_id = user["id"]

    while True:
        clear_terminal()
        header()
        print(f"\n=== MENU SURVEYOR (Login sebagai: {user['username']}) ===")
        print("1. Survey lahan yang sudah ada")
        print("2. Input tanaman baru")
        print("3. Update profile saya")
        print("0. Logout")

        pilihan = input("Pilih menu: ").strip()

        # 1. SURVEY LAHAN
        if pilihan == "1":
            # tampilkan lahan yang bisa diakses surveyor ini
            lihat_lahan_universal(conn, user)

            print("\n=== Input survey ===")
            try:
                lahan_id = int(input("ID lahan yang disurvey: ").strip())
            except ValueError:
                print("ID lahan harus angka.")
                enter_break()
                continue

            claim = claim_lahan_for_surveyor(conn, lahan_id, surveyor_id)
            if not claim:
                print("⚠️ Lahan ini sudah diambil surveyor lain atau tidak ada.")
                enter_break()
                continue

            # pilih iklim
            iklim_list = get_all_iklim(conn)
            if not iklim_list:
                print("Belum ada data iklim, isi dulu tabel iklim.")
                enter_break()
                continue

            print("\nPilih Iklim:")
            for iklim_id, jenis_cuaca in iklim_list:
                print(f"  {iklim_id}. {jenis_cuaca}")

            try:
                id_iklim = int(input("ID Iklim: ").strip())
            except ValueError:
                print("ID iklim harus angka.")
                enter_break()
                continue

            # pilih kondisi tanah
            tanah_list = get_all_kondisi_tanah(conn)
            if not tanah_list:
                print("Belum ada data kondisi tanah, isi dulu tabel kondisi_tanah.")
                enter_break()
                continue

            print("\nPilih Kondisi Tanah:")
            for tanah_id, kondisi, ph, nutrisi, kelembapan in tanah_list:
                print(
                    f"  {tanah_id}. {kondisi} (pH={ph}, Nutrisi={nutrisi}, "
                    f"Kelembapan={kelembapan})"
                )

            try:
                id_tanah = int(input("ID Kondisi Tanah: ").strip())
            except ValueError:
                print("ID kondisi tanah harus angka.")
                enter_break()
                continue

            # optional: rekomendasikan tanaman
            id_tanaman = None
            nama_tanaman_manual = None

            jawab = input("\nIngin merekomendasikan tanaman dari daftar? (y/n): ").strip().lower()
            if jawab == "y":
                # pilih tipe tanaman
                tipe_list = get_all_tipe_tanaman(conn)
                if not tipe_list:
                    print("Belum ada tipe_tanaman, isi dulu.")
                    enter_break()
                    continue

                print("\nTipe Tanaman:")
                for tipe_id, jenis in tipe_list:
                    print(f"  {tipe_id}. {jenis}")

                try:
                    id_tipe = int(input("ID Tipe Tanaman: ").strip())
                except ValueError:
                    print("ID tipe tanaman harus angka.")
                    enter_break()
                    continue

                tanaman_list = get_tanaman_by_tipe(conn, id_tipe)
                if not tanaman_list:
                    print("Belum ada tanaman untuk tipe ini.")
                else:
                    print(f"\nTanaman (Tipe {id_tipe}):")
                    for t_id, t_nama in tanaman_list:
                        print(f"  {t_id}. {t_nama}")

                    try:
                        id_tanaman = int(input("ID Tanaman yang direkomendasikan: ").strip())
                    except ValueError:
                        print("ID tanaman harus angka.")
                        enter_break()
                        continue
            else:
                # kalau tidak pilih dari daftar, boleh isi nama bebas (opsional)
                isi_manual = input("Ingin isi nama tanaman manual? (y/n): ").strip().lower()
                if isi_manual == "y":
                    nama_tanaman_manual = input("Nama tanaman (free text): ").strip() or None

            # simpan ke survey_data (ikut signature baru)
            survey_id = add_survey_data(
                conn=conn,
                id_lahan=lahan_id,
                id_user_surveyor=surveyor_id,
                id_user_admin=None,          # bisa diisi nanti oleh admin
                id_iklim=id_iklim,
                id_tanah=id_tanah,
                nama_tanaman=nama_tanaman_manual,
                id_tanaman=id_tanaman,
                status_survey="waiting",
            )

            if survey_id is not None:
                print(
                    f"✅ Survey baru dengan ID {survey_id} berhasil ditambahkan "
                    f"untuk lahan {lahan_id}."
                )
            else:
                print("⚠️ Gagal menambahkan survey.")
            enter_break()

        # 2. INPUT TANAMAN BARU
        elif pilihan == "2":
            print("\n=== Input tanaman baru ===")

            # pilih tipe tanaman
            tipe_list = get_all_tipe_tanaman(conn)
            if not tipe_list:
                print("Belum ada data tipe_tanaman, isi dulu tabel tipe_tanaman.")
                enter_break()
                continue

            print("\nTipe Tanaman:")
            for tipe_id, jenis in tipe_list:
                print(f"  {tipe_id}. {jenis}")

            try:
                id_tipe_tanaman = int(input("ID Tipe Tanaman: ").strip())
            except ValueError:
                print("ID tipe tanaman harus angka.")
                enter_break()
                continue

            nama_tanaman = input("Nama tanaman: ").strip()
            if not nama_tanaman:
                print("Nama tanaman tidak boleh kosong.")
                enter_break()
                continue

            tanaman_id = add_tanaman(conn, id_tipe_tanaman, nama_tanaman)

            if tanaman_id is None:
                print("⚠️ Tanaman sudah ada atau gagal ditambahkan.")
            else:
                print(f"✅ Tanaman berhasil ditambah dengan ID {tanaman_id}")
            enter_break()

        elif pilihan == "3":
            menu_update_profile(conn, user)
            enter_break()

        elif pilihan == "0":
            print("Logout dari surveyor.")
            break
        else:
            print("Pilihan tidak valid, coba lagi.")
            enter_break()


def menu_update_profile(conn, user: dict[str, str | int]) -> None:
    """
    Menu update profil untuk user yang sedang login (petani / surveyor).
    """
    user_id = user["id"]
    current = get_user_by_id(conn, user_id)

    if not current:
        print("Data user tidak ditemukan.")
        return

    print("\n=== Update Profil Saya ===")
    print(f"Username (tidak bisa diubah): {current['username']}")
    print(f"Nama sekarang     : {display(current['name'])}")
    print(f"Email sekarang    : {display(current['email'])}")
    print(f"No. Telp sekarang : {display(current['no_telp'])}")
    print(f"ID Alamat sekarang: {display(current['id_alamat'])}")

    print("\nKosongkan (Enter) jika tidak ingin mengubah field tertentu.\n")

    # ambil input baru, kosong = keep
    new_name = input_optional(f"Nama baru [{current['name']}]: ", current["name"])
    new_email = input_optional(f"Email baru [{current['email']}]: ", current["email"])
    new_no_telp = input_optional(f"No. Telp baru [{current['no_telp']}]: ", current["no_telp"])

    pw_raw = input("Password baru (kosongkan jika tidak diubah): ").strip()
    new_password = pw_raw or None

    ubah_alamat = input("Ingin mengubah alamat? (y/n): ").strip().lower()
    new_id_alamat = current["id_alamat"]

    if ubah_alamat == "y":
        alamat_id_baru = pilih_alamat_baru(conn)
        if alamat_id_baru is not None:
            new_id_alamat = alamat_id_baru

    updated = update_user_profile(
        conn,
        user_id=user_id,
        name=new_name,
        email=new_email,
        no_telp=new_no_telp,
        password=new_password,
        id_alamat=new_id_alamat,
    )

    if updated:
        print("✅ Profil berhasil diperbarui.")
        # update juga dict user yang lagi login kalau nama/username kepakai di header
        user["username"] = current["username"]
    else:
        print("⚠️ Tidak ada perubahan pada profil.")