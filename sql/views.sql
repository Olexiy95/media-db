-- Movie table view
CREATE VIEW
    v_movie_table AS
SELECT
    md.id AS media_id,
    mv.id as movie_id,
    md.title AS title,
    md.sort_title AS sort_title,
    md.rating AS rating,
    mv.year AS year,
    (
        select
            name
        from
            directors
        where
            id = mv.director
    ) AS director,
    (
        SELECT
            GROUP_CONCAT (name, ', ')
        FROM
            (
                SELECT DISTINCT
                    g.name AS name
                FROM
                    movie_genre_relationship mgr2
                    JOIN genres g ON g.id = mgr2.genre_id
                WHERE
                    mgr2.movie_id = mv.id
                ORDER BY
                    LOWER(g.name)
            )
    ) AS genre,
    (
        SELECT
            GROUP_CONCAT (name, ', ')
        FROM
            (
                SELECT
                    a.name AS name
                FROM
                    actor_movie_relationship amr2
                    JOIN actors a ON a.id = amr2.actor_id
                WHERE
                    amr2.movie_id = mv.id
                ORDER BY
                    amr2.billing_order,
                    LOWER(a.name)
            )
    ) AS "leading_actors",
    CASE
        WHEN md.obtained = 1 THEN 'Yes'
        ELSE 'No'
    END AS obtained
FROM
    media md
    LEFT JOIN movies mv ON md.id = mv.media_id
WHERE
    md.type = 'movie'
    -- ORDER BY
    --     md.sort_title COLLATE NOCASE ASC;
    -- Actor page view
create view
    v_actor_page AS
SELECT
    a.id AS actor_id,
    a.name,
    a.pseudonym,
    -- movie side
    mm.id AS movie_media_id,
    mo.id AS movie_id,
    mo.year,
    -- show side
    ms.id AS show_media_id,
    s.id AS show_id,
    s.start_year,
    s.end_year,
    COALESCE(mm.title, ms.title) AS title,
    COALESCE(mm.sort_title, ms.sort_title) AS sort_title,
    COALESCE(mm.type, ms.type) AS type
FROM
    actors a
    LEFT JOIN actor_movie_relationship am ON am.actor_id = a.id
    LEFT JOIN movies mo ON mo.id = am.movie_id
    LEFT JOIN media mm ON mm.id = mo.media_id
    LEFT JOIN actor_show_relationship asr ON asr.actor_id = a.id
    LEFT JOIN shows s ON s.id = asr.show_id
    LEFT JOIN media ms ON ms.id = s.media_id;

CREATE VIEW
    v_show_table AS
SELECT
    md.id AS media_id,
    s.id AS show_id,
    md.title AS title,
    md.sort_title AS sort_title,
    md.rating AS rating,
    s.start_year AS start_year,
    s.end_year AS end_year,
    (
        SELECT
            name
        FROM
            show_networks
        WHERE
            id = s.network
    ) AS network,
    (
        SELECT
            GROUP_CONCAT (name, ', ')
        FROM
            (
                SELECT DISTINCT
                    g.name AS name
                FROM
                    show_genre_relationship sgr2
                    JOIN genres g ON g.id = sgr2.genre_id
                WHERE
                    sgr2.show_id = s.id
                ORDER BY
                    LOWER(g.name)
            )
    ) AS genre,
    (
        SELECT
            GROUP_CONCAT (name, ', ')
        FROM
            (
                SELECT
                    a.name AS name
                FROM
                    actor_show_relationship asr2
                    JOIN actors a ON a.id = asr2.actor_id
                WHERE
                    asr2.show_id = s.id
                ORDER BY
                    asr2.billing_order,
                    LOWER(a.name)
            )
    ) AS "leading_actors",
    CASE
        WHEN md.obtained = 1 THEN 'Yes'
        ELSE 'No'
    END AS obtained
FROM
    media md
    LEFT JOIN shows s ON md.id = s.media_id
WHERE
    md.type = 'show'
ORDER BY
    md.sort_title COLLATE NOCASE ASC;

-- Collections combination view
CREATE VIEW
    v_collections AS
SELECT
    mc.id AS collection_id,
    mc.name AS collection_name,
    'movie' AS type,
    m.id AS media_id,
    m.title AS title,
    m.sort_title AS sort_title,
    mv.year AS year
FROM
    movie_collections mc
    LEFT JOIN movie_collection_relationship mcr ON mcr.collection_id = mc.id
    LEFT JOIN movies mv ON mv.id = mcr.movie_id
    LEFT JOIN media m ON m.id = mv.media_id
UNION ALL
SELECT
    sc.id AS collection_id,
    sc.name AS collection_name,
    'show' AS type,
    m.id AS media_id,
    m.title AS title,
    m.sort_title AS sort_title,
    s.start_year AS year
FROM
    show_collections sc
    LEFT JOIN show_collection_relationship scr ON scr.collection_id = sc.id
    LEFT JOIN shows s ON s.id = scr.show_id
    LEFT JOIN media m ON m.id = s.media_id
ORDER BY
    collection_name COLLATE NOCASE,
    sort_title COLLATE NOCASE;