import psycopg2
from datetime import date

class LahanCRUD:
    def __init__(self, db_config):
        self.conn = psycopg2.connect(**db_config)
        self.cursor = self.conn.cursor()

    def add_user(self, username, password, role):
        query = "INSERT INTO users (username, password, role) VALUES (%s, %s, %s) RETURNING user_id"
        self.cursor.execute(query, (username, password, role))
        user_id = self.cursor.fetchone()[0]
        self.conn.commit()
        return user_id

    def add_lahan(self, petani_id, lokasi, ketinggian, ph, tekstur, kandungan_nutrisi, suhu, curah_hujan):
        tanggal_input = date.today()
        query = '''
            INSERT INTO lahan (petani_id, lokasi, ketinggian, ph, tekstur, kandungan_nutrisi, suhu, curah_hujan, tanggal_input)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING lahan_id
        '''
        self.cursor.execute(query, (petani_id, lokasi, ketinggian, ph, tekstur, kandungan_nutrisi, suhu, curah_hujan, tanggal_input))
        lahan_id = self.cursor.fetchone()[0]
        self.conn.commit()
        return lahan_id

    def add_tanaman(self, nama, deskripsi=None):
        query = "INSERT INTO tanaman (nama, deskripsi) VALUES (%s, %s) RETURNING tanaman_id"
        self.cursor.execute(query, (nama, deskripsi))
        tanaman_id = self.cursor.fetchone()[0]
        self.conn.commit()
        return tanaman_id

    def close(self):
        self.cursor.close()
        self.conn.close()

if __name__ == '__main__':
    db_config = {
        'host': 'localhost',
        'database': 'ProjekUAS',
        'user': 'postgres',
        'password': '23'
    }
    crud = LahanCRUD(db_config)

    print("Input data petani:")
    username = input("Username: ")
    password = input("Password: ")
    role = 'petani'  # karena input khusus petani
    petani_id = crud.add_user(username, password, role)
    print(f"Petani dengan ID {petani_id} berhasil ditambahkan.")

    print("Input data lahan petani:")
    lokasi = input("Lokasi lahan: ")
    ketinggian = float(input("Ketinggian (meter): "))
    ph = float(input("pH tanah: "))
    tekstur = input("Tekstur tanah: ")
    kandungan_nutrisi = input("Kandungan nutrisi: ")
    suhu = float(input("Suhu (°C): "))
    curah_hujan = float(input("Curah hujan (mm): "))
    lahan_id = crud.add_lahan(petani_id, lokasi, ketinggian, ph, tekstur, kandungan_nutrisi, suhu, curah_hujan)
    print(f"Lahan dengan ID {lahan_id} berhasil ditambahkan.")

    print("Input data tanaman:")
    nama_tanaman = input("Nama tanaman: ")
    deskripsi_tanaman = input("Deskripsi tanaman (boleh kosong): ")
    tanaman_id = crud.add_tanaman(nama_tanaman, deskripsi_tanaman if deskripsi_tanaman else None)
    print(f"Tanaman dengan ID {tanaman_id} berhasil ditambahkan.")

    crud.close()
    print("Proses inputn data selesai.")