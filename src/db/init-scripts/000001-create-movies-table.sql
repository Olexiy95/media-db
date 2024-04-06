CREATE TABLE
    IF NOT EXISTS movies (
        id VARCHAR(8) PRIMARY KEY,
        title VARCHAR(255) NOT NULL,
        director VARCHAR(255),
        year INTEGER
    );

INSERT INTO
    movies (id, title, director, year)
VALUES
    (
        'm1a2b3c4',
        'Inception',
        'Christopher Nolan',
        2010
    ),
    (
        'm5d6e7f8',
        'The Matrix',
        'Lana Wachowski, Lilly Wachowski',
        1999
    ),
    (
        'm9g0h1i2',
        'Interstellar',
        'Christopher Nolan',
        2014
    );