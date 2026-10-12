CREATE TABLE gempa_bmkg (
    datetime_utc TIMESTAMPTZ PRIMARY KEY,
    tanggal      VARCHAR(20),
    jam          VARCHAR(20),
    coordinates  VARCHAR(30),
    magnitude    FLOAT,
    kedalaman    VARCHAR(20),
    wilayah      TEXT,
    potensi      VARCHAR(50),
);
