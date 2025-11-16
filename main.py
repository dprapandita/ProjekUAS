import utils.database_connection
from core.auth import signup, login
from utils.header import header
from utils.menus import menu_admin, menu_petani, menu_surveyor

if __name__ == '__main__':
    conn = utils.database_connection.get_connection()

    try:
        while True:
            header()
            print("1. Login")
            print("2. Registrasi user baru")
            print("0. Keluar")

            pilihan = input("Pilih menu: ").strip()

            if pilihan == "1":
                user = login(conn)
                match user['role']:
                    case "admin":
                        menu_admin(conn, user)
                    case "petani":
                        menu_petani(conn, user)
                    case "surveyor":
                        menu_surveyor(conn, user)
                    case Exception as e:
                        print(f"Ada kesalahan :{e}")


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