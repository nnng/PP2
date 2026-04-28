-- =========================================
-- FUNCTION 1: Search contacts by pattern
-- =========================================
CREATE OR REPLACE FUNCTION search_contacts(p_query TEXT)
RETURNS TABLE(
    id INT,
    name VARCHAR,
    surname VARCHAR,
    email VARCHAR,
    birthday DATE,
    group_name VARCHAR,
    created_at TIMESTAMP,
    phones_json TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        c.id,
        c.name,
        c.surname,
        c.email,
        c.birthday,
        COALESCE(g.name, 'Other') AS group_name,
        c.created_at,
        COALESCE(
            json_agg(json_build_object('phone', p.phone, 'type', p.type) ORDER BY p.id)
                FILTER (WHERE p.id IS NOT NULL),
            '[]'::json
        )::TEXT AS phones_json
    FROM contacts c
    LEFT JOIN groups g ON g.id = c.group_id
    LEFT JOIN phones p ON p.contact_id = c.id
    WHERE c.name ILIKE '%' || p_query || '%'
       OR c.surname ILIKE '%' || p_query || '%'
       OR COALESCE(c.email, '') ILIKE '%' || p_query || '%'
       OR EXISTS (
            SELECT 1
            FROM phones px
            WHERE px.contact_id = c.id
              AND px.phone ILIKE '%' || p_query || '%'
       )
    GROUP BY c.id, g.name
    ORDER BY c.name, c.surname;
END;
$$ LANGUAGE plpgsql;


-- =========================================
-- FUNCTION 1B: Backward-compatible alias
-- =========================================
CREATE OR REPLACE FUNCTION search_phonebook(p_pattern TEXT)
RETURNS TABLE(
    id INT,
    name VARCHAR,
    surname VARCHAR,
    email VARCHAR,
    birthday DATE,
    group_name VARCHAR,
    created_at TIMESTAMP,
    phones_json TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT *
    FROM search_contacts(p_pattern);
END;
$$ LANGUAGE plpgsql;


-- =========================================
-- FUNCTION 2: Get contacts with pagination
-- =========================================
CREATE OR REPLACE FUNCTION get_phonebook_paginated(p_limit INT, p_offset INT)
RETURNS TABLE(
    id INT,
    name VARCHAR,
    surname VARCHAR,
    email VARCHAR,
    birthday DATE,
    group_name VARCHAR,
    created_at TIMESTAMP,
    phones_json TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        c.id,
        c.name,
        c.surname,
        c.email,
        c.birthday,
        COALESCE(g.name, 'Other') AS group_name,
        c.created_at,
        COALESCE(
            json_agg(json_build_object('phone', p.phone, 'type', p.type) ORDER BY p.id)
                FILTER (WHERE p.id IS NOT NULL),
            '[]'::json
        )::TEXT AS phones_json
    FROM contacts c
    LEFT JOIN groups g ON g.id = c.group_id
    LEFT JOIN phones p ON p.contact_id = c.id
    GROUP BY c.id, g.name
    ORDER BY c.id
    LIMIT p_limit OFFSET p_offset;
END;
$$ LANGUAGE plpgsql;


-- =========================================
-- FUNCTION 3: Alias with the same behavior
-- =========================================
CREATE OR REPLACE FUNCTION get_contacts_paginated(p_limit INT, p_offset INT)
RETURNS TABLE(
    id INT,
    name VARCHAR,
    surname VARCHAR,
    email VARCHAR,
    birthday DATE,
    group_name VARCHAR,
    created_at TIMESTAMP,
    phones_json TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT *
    FROM get_phonebook_paginated(p_limit, p_offset);
END;
$$ LANGUAGE plpgsql;