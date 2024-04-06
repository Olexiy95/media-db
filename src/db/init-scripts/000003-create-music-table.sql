CREATE TABLE
    music (
        id VARCHAR(8) PRIMARY KEY,
        title VARCHAR(255) NOT NULL,
        artist VARCHAR(255),
        year INTEGER
    );

INSERT INTO
    music (id, title, artist, year)
VALUES
    ('mu1a2b3c', 'Shape of You', 'Ed Sheeran', 2017),
    ('mu5d6e7f', 'Believer', 'Imagine Dragons', 2017);