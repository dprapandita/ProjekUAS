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

CREATE TABLE IF NOT EXISTS users(
    user_id SERIAL PRIMARY KEY NOT NULL,
    name VARCHAR(200) NOT NULL,
    username VARCHAR(100) NOT NULL,
    password VARCHAR(20) NOT NULL,
    email VARCHAR(50) UNIQUE NULL,
    no_telp VARCHAR(13) UNIQUE NULL,
    pembuatan TIMESTAMP default now()::DATE
);

CREATE TABLE IF NOT EXISTS roles(
    role_id SERIAL PRIMARY KEY NOT NULL,
    nama_role VARCHAR(100) NOT NULL,
    pembuatan TIMESTAMP default now()::DATE
);

CREATE TABLE IF NOT EXISTS user_roles(
    user_role_id SERIAL PRIMARY KEY NOT NULL,
    id_user INTEGER REFERENCES users(user_id),
    id_role INTEGER REFERENCES roles(role_id)
);

CREATE TABLE IF NOT EXISTS iklim(
    iklim_id SERIAL PRIMARY KEY,
    jenis_cuaca VARCHAR(20) NOT NULL
);

CREATE TABLE IF NOT EXISTS kondisi_tanah(
    kondisi_tanah_id SERIAL PRIMARY KEY,
    kondisi_tanah VARCHAR(20) NOT NULL,
    ph FLOAT NOT NULL,
    kandungan_nutrisi FLOAT NOT NULL,
    kelembapan FLOAT NOT NULL
);

-- Insert data default
INSERT INTO users (name, username, password) VALUES
('Admin Ejak', 'ejak', '23'),
('Petani Divo', 'divo', '23'),
('Surveyor Zera', 'zera', '23');

-- Insert roles
INSERT INTO roles (nama_role) VALUES ('admin'), ('petani'), ('surveyor');

CREATE TABLE IF NOT EXISTS lahan (
    lahan_id SERIAL PRIMARY KEY,
    id_user_surveyor INTEGER REFERENCES users(user_id),
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
    id_user INTEGER REFERENCES users(user_id),
    nama VARCHAR(100) NOT NULL
);

CREATE TABLE IF NOT EXISTS survey_data (
    survey_id SERIAL PRIMARY KEY,
    nama_tanaman VARCHAR(50),
    id_user_surveyor INTEGER REFERENCES users(user_id),
    id_user_admin INTEGER REFERENCES users(user_id),
    id_lahan INTEGER REFERENCES lahan(lahan_id),
    id_iklim INTEGER REFERENCES iklim(iklim_id),
    id_tanah INTEGER REFERENCES  kondisi_tanah(kondisi_tanah_id),
    status_survey VARCHAR(15) default 'waiting',
    id_tanaman INTEGER REFERENCES tanaman(tanaman_id),
    tanggal_survey DATE DEFAULT now()::DATE
);

CREATE TABLE IF NOT EXISTS penanaman (
    penanaman_id SERIAL PRIMARY KEY,
    id_survey INTEGER REFERENCES survey_data(survey_id),
    tanggal_penanaman DATE
);