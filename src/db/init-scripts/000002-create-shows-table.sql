CREATE TABLE
    shows (
        id VARCHAR(8) PRIMARY KEY,
        title VARCHAR(255) NOT NULL,
        creator VARCHAR(255),
        seasons INTEGER
    );

INSERT INTO
    shows (id, title, creator, seasons)
VALUES
    (
        's1a2b3c4',
        'Stranger Things',
        'The Duffer Brothers',
        4
    ),
    ('s5d6e7f8', 'Breaking Bad', 'Vince Gilligan', 5),
    (
        's9g0h1i2',
        'Game of Thrones',
        'David Benioff, D.B. Weiss',
        8
    );