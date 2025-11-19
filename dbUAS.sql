CREATE TABLE provinsi (
    provinsi_id   SERIAL PRIMARY KEY,
    nama_provinsi VARCHAR(150) NOT NULL
);

CREATE TABLE kota (
    kota_id   SERIAL PRIMARY KEY,
    nama_kota VARCHAR(100)
);

CREATE TABLE kecamatan (
    kecamatan_id   SERIAL PRIMARY KEY,
    nama_kecamatan VARCHAR(200)
);

CREATE TABLE alamat (
    alamat_id     SERIAL PRIMARY KEY,
    nama_jalan    VARCHAR(100) NOT NULL,
    id_kota       INTEGER REFERENCES kota(kota_id),
    id_kecamatan  INTEGER REFERENCES kecamatan(kecamatan_id),
    id_provinsi   INTEGER REFERENCES provinsi(provinsi_id)
);

-- Tabel admin
CREATE TABLE IF NOT EXISTS admin (
    admin_id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(100) NOT NULL
);

-- Tabel surveyor
CREATE TABLE IF NOT EXISTS surveyor (
    surveyor_id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(100) NOT NULL
);

-- Tabel petani
CREATE TABLE IF NOT EXISTS petani (
    petani_id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(100) NOT NULL
);

CREATE TABLE IF NOT EXISTS iklim(
    iklim_id SERIAL PRIMARY KEY,
    jenis_cuaca VARCHAR(20) NOT NULL
);

CREATE TABLE IF NOT EXISTS kondisi_tanah(
    kondisi_tanah_id SERIAL PRIMARY KEY,
    kondisi_tanah VARCHAR(20) NOT NULL
);

-- Insert data default
INSERT INTO admin (username, password) VALUES ('ejak', '23');
INSERT INTO petani (username, password) VALUES ('divo', '23');
INSERT INTO surveyor (username, password) VALUES ('zera', '23');

CREATE TABLE IF NOT EXISTS lahan (
    lahan_id SERIAL PRIMARY KEY,
    id_petani INTEGER REFERENCES petani(petani_id),
    id_alamat INTEGER REFERENCES alamat(alamat_id),
    ketinggian REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS tipe_tanaman(
    tipe_tanaman_id SERIAL PRIMARY KEY,
    jenis_tanaman VARCHAR(20) NOT NULL
);

CREATE TABLE IF NOT EXISTS tanaman (
    tanaman_id SERIAL PRIMARY KEY,
    id_tipe_tanaman INTEGER REFERENCES tipe_tanaman(tipe_tanaman_id),
    id_admin INTEGER REFERENCES admin(admin_id),
    nama VARCHAR(100) NOT NULL,
    deskripsi TEXT NULL
);

CREATE TABLE IF NOT EXISTS survey_data (
    survey_id SERIAL PRIMARY KEY,
    nama_tanaman VARCHAR(50),
    id_surveyor INTEGER REFERENCES surveyor(surveyor_id),
    id_lahan INTEGER REFERENCES lahan(lahan_id),
    id_iklim INTEGER REFERENCES iklim(iklim_id),
    id_tanah INTEGER REFERENCES  kondisi_tanah(kondisi_tanah_id),
    status_survey VARCHAR(10) default 'waiting',
    tanggal_survey DATE DEFAULT now()::DATE,
    id_tanaman INTEGER REFERENCES tanaman(tanaman_id)
);

CREATE TABLE IF NOT EXISTS penanaman (
    penanaman_id SERIAL PRIMARY KEY,
    lahan_id INTEGER REFERENCES lahan(lahan_id),
    tanaman_id INTEGER REFERENCES tanaman(tanaman_id),
    tanggal_tanam DATE
);

-- ALTER TABLE lahan ADD COLUMN admin_id integer REFERENCES admin(admin_id);

ALTER TABLE survey_data ADD COLUMN admin_id integer REFERENCES admin(admin_id);

ALTER TABLE petani ADD COLUMN admin_id integer REFERENCES admin(admin_id);

ALTER TABLE surveyor ADD COLUMN admin_id integer REFERENCES admin(admin_id);