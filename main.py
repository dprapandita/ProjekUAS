import utils.database_connection
from core.auth import signup, login
from utils.header import header, clear_terminal
from utils.menus import menu_admin, menu_petani, menu_surveyor

if __name__ == '__main__':
    conn = utils.database_connection.get_connection()
    clear_terminal()
    try:
        while True:
            header()
            print("1. Login")
            print("2. Registrasi user baru")
            print("0. Keluar")

            pilihan = input("Pilih menu: ").strip()

            if pilihan == "1":
                user = login(conn)
                if not user:
                    # Login gagal, kembali ke menu utama
                    continue
                role = user.get('role')
                if role == "admin":
                    menu_admin(conn, user)
                elif role == "petani":
                    menu_petani(conn, user)
                elif role == "surveyor":
                    menu_surveyor(conn, user)
                else:
                    print("Role tidak dikenali.")


            elif pilihan == "2":
                signup(conn)
            elif pilihan == "0":
                print("Keluar dari program")
                break
            else:
                print("Pilihan tidak valid, coba lagi")
    except KeyboardInterrupt:
        conn.close()
        print("\nKeluar dari program secara paksa")
        exit(0)
    finally:
        conn.close()