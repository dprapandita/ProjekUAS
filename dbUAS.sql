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

-- Insert data admin default
INSERT INTO admin (username, password) VALUES ('ejak', '23');

CREATE TABLE IF NOT EXISTS lahan (
    lahan_id SERIAL PRIMARY KEY,
    petani_id INTEGER REFERENCES petani(petani_id),
    lokasi VARCHAR(100),
    ketinggian REAL,
    ph REAL,
    tekstur VARCHAR(50),
    kandungan_nutrisi VARCHAR(100),
    suhu REAL,
    curah_hujan REAL,
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
