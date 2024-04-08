CREATE TABLE
    IF NOT EXISTS movies (
        id VARCHAR(8) PRIMARY KEY,
        title VARCHAR(255) NOT NULL,
        year INTEGER,
        genre VARCHAR(255),
        lead_actors VARCHAR(255),
        rating DECIMAL(2, 1) CHECK (
            rating >= 1
            AND rating <= 10
        ),
        comments TEXT,
        director VARCHAR(255),
    );

INSERT INTO
    movies (
        id,
        title,
        year,
        genre,
        lead_actors,
        rating,
        comments,
        director
    )
VALUES
    (
        '1',
        'Movie 1',
        2020,
        'Action',
        'Actor 1, Actor 2',
        8.5,
        'Great movie!',
        'Director 1'
    ),
    (
        '2',
        'Movie 2',
        2018,
        'Drama',
        'Actor 3, Actor 4',
        7.9,
        'Nice storyline',
        'Director 2'
    ),
    (
        '3',
        'Movie 3',
        2019,
        'Comedy',
        'Actor 5, Actor 6',
        6.7,
        'Funny movie',
        'Director 3'
    );