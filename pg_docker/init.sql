CREATE TABLE IF NOT EXISTS reviews (
    id SERIAL PRIMARY KEY,
    polarity INTEGER,
    title TEXT,
    text TEXT
);

COPY reviews(polarity, title, text)
FROM '/docker-entrypoint-initdb.d/init.csv'
DELIMITER ','
CSV;