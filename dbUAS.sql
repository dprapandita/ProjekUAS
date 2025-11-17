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
    password VARCHAR(100) NOT NULL,
    id_kecamatan INTEGER REFERENCES kecamatan(kecamatan_id)
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

-- Insert data default
INSERT INTO admin (username, password) VALUES ('ejak', '23');
INSERT INTO petani (username, password) VALUES ('divo', '23');
INSERT INTO surveyor (username, password) VALUES ('zera', '23');

CREATE TABLE IF NOT EXISTS lahan (
    lahan_id SERIAL PRIMARY KEY,
    petani_id INTEGER REFERENCES petani(petani_id),
    ketinggian REAL,
    tanah VARCHAR(50),
    iklim VARCHAR(50),
    tanggal_input DATE
);

CREATE TABLE IF NOT EXISTS tanaman (
    tanaman_id SERIAL PRIMARY KEY,
    nama VARCHAR(100) NOT NULL,
    deskripsi TEXT
);

CREATE TABLE IF NOT EXISTS penanaman (
    penanaman_id SERIAL PRIMARY KEY,
    lahan_id INTEGER REFERENCES lahan(lahan_id),
    tanaman_id INTEGER REFERENCES tanaman(tanaman_id),
    tanggal_tanam DATE
);

CREATE TABLE IF NOT EXISTS survey_data (
    survey_id SERIAL PRIMARY KEY,
    lahan_id INTEGER REFERENCES lahan(lahan_id),
    surveyor_id INTEGER REFERENCES surveyor(surveyor_id),
    hasil_survey TEXT,
    tanggal_survey DATE
);

ALTER TABLE lahan ADD COLUMN admin_id integer REFERENCES admin(admin_id);

ALTER TABLE penanaman ADD COLUMN admin_id integer REFERENCES admin(admin_id);

ALTER TABLE survey_data ADD COLUMN admin_id integer REFERENCES admin(admin_id);

ALTER TABLE petani ADD COLUMN admin_id integer REFERENCES admin(admin_id);

ALTER TABLE surveyor ADD COLUMN admin_id integer REFERENCES admin(admin_id);