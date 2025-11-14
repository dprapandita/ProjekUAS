import psycopg2

class UserAuthSystemPG:
    def __init__(self, db_config):
        self.conn = psycopg2.connect(**db_config)
        self.cursor = self.conn.cursor()
        self.current_user = None

    def signup(self):
        print("\n=== Sign Up ===")
        role = None
        while role not in ['surveyor', 'petani']:
            role = input("Daftar sebagai (surveyor/petani): ").strip().lower()
            if role not in ['surveyor', 'petani']:
                print("Role harus 'surveyor' atau 'petani'.")

        username = input("Username: ").strip()
        password = input("Password: ").strip()

        table_name = role  # tabel surveyor atau petani

        # Cek apakah username sudah ada
        self.cursor.execute(f"SELECT * FROM {table_name} WHERE username = %s", (username,))
        if self.cursor.fetchone():
            print("Username sudah terdaftar, coba username lain.")
            return

        # Insert user baru
        self.cursor.execute(f"INSERT INTO {table_name} (username, password) VALUES (%s, %s)", (username, password))
        self.conn.commit()
        print(f"User {username} berhasil didaftarkan sebagai {role}.")

    def login(self):
        print("\n=== Login ===")
        role = None
        while role not in ['admin', 'surveyor', 'petani']:
            role = input("Login sebagai (admin/surveyor/petani): ").strip().lower()
            if role not in ['admin', 'surveyor', 'petani']:
                print("Role harus salah satu dari: admin, surveyor, petani")

        username = input("Username: ").strip()
        password = input("Password: ").strip()

        table_name = ''
        if role == 'admin':
            table_name = 'admin'
        elif role == 'surveyor':
            table_name = 'surveyor'
        else:
            table_name = 'petani'

        query = f"SELECT * FROM {table_name} WHERE username = %s AND password = %s"
        self.cursor.execute(query, (username, password))
        result = self.cursor.fetchone()

        if result:
            self.current_user = {'role': role, 'username': username}
            print(f"Login berhasil! Anda masuk sebagai {role}: {username}")
        else:
            print("Login gagal! Username atau password salah.")

    def logout(self):
        if self.current_user:
            print(f"User {self.current_user['username']} logout.")
            self.current_user = None
        else:
            print("Belum login.")

    def run(self):
        while True:
            print("\n=== Menu ===")
            print("1. Sign Up (Surveyor/Petani)")
            print("2. Login")
            print("3. Log Out")
            print("4. Exit")
            choice = input("Pilih menu: ").strip()

            if choice == '1':
                if self.current_user:
                    print("Logout dulu sebelum daftar user baru.")
                else:
                    self.signup()
            elif choice == '2':
                if self.current_user:
                    print("Anda sudah login. Silakan logout dulu.")
                else:
                    self.login()
            elif choice == '3':
                self.logout()
            elif choice == '4':
                print("Keluar dari program.")
                break
            else:
                print("Pilihan tidak valid.")

    def close(self):
        self.cursor.close()
        self.conn.close()

if __name__ == '__main__':
    db_config = {
        'host': 'localhost',
        'database': 'ProjekUAS',
        'user': 'postgres',
        'password': '23',
        'port': 5432
    }
    system = UserAuthSystemPG(db_config)
    try:
        system.run()
    finally:
        system.close()
