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

-- Insert data admin default sesuai permintaan
INSERT INTO admin (username, password) VALUES ('ejak', '23')
ON CONFLICT (username) DO NOTHING;
