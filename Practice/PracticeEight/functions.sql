-- =========================================
-- FUNCTION 1: Search contacts by pattern
-- =========================================
CREATE OR REPLACE FUNCTION search_phonebook(p_pattern TEXT)
RETURNS TABLE(
    id INT,
    name VARCHAR,
    surname VARCHAR,
    phone VARCHAR
) AS $$
BEGIN
    RETURN QUERY
    SELECT pb.id, pb.name, pb.surname, pb.phone
    FROM phonebook pb
    WHERE pb.name ILIKE '%' || p_pattern || '%'
       OR pb.surname ILIKE '%' || p_pattern || '%'
       OR pb.phone ILIKE '%' || p_pattern || '%';
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
    phone VARCHAR
) AS $$
BEGIN
    RETURN QUERY
    SELECT pb.id, pb.name, pb.surname, pb.phone
    FROM phonebook pb
    ORDER BY pb.id
    LIMIT p_limit OFFSET p_offset;
END;
$$ LANGUAGE plpgsql;