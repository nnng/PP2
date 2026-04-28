-- =========================================
-- PROCEDURE 1: Insert or update one contact
-- =========================================
CREATE OR REPLACE PROCEDURE upsert_contact(
    p_name VARCHAR,
    p_surname VARCHAR,
    p_phone VARCHAR DEFAULT NULL,
    p_phone_type VARCHAR DEFAULT 'mobile',
    p_email VARCHAR DEFAULT NULL,
    p_birthday DATE DEFAULT NULL,
    p_group_name VARCHAR DEFAULT NULL
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_contact_id INTEGER;
    v_group_id INTEGER;
    v_group_name VARCHAR(50);
    v_phone_type VARCHAR(10);
BEGIN
    v_phone_type := LOWER(COALESCE(NULLIF(TRIM(p_phone_type), ''), 'mobile'));

    IF v_phone_type NOT IN ('home', 'work', 'mobile') THEN
        RAISE EXCEPTION 'Invalid phone type: %', p_phone_type;
    END IF;

    v_group_name := NULLIF(TRIM(p_group_name), '');
    IF v_group_name IS NULL THEN
        v_group_name := 'Other';
    END IF;

    INSERT INTO groups(name)
    VALUES (v_group_name)
    ON CONFLICT (name) DO NOTHING;

    SELECT id INTO v_group_id
    FROM groups
    WHERE name = v_group_name;

    IF EXISTS (
        SELECT 1
        FROM contacts
        WHERE name = p_name AND surname = p_surname
    ) THEN
        UPDATE contacts
        SET email = COALESCE(p_email, email),
            birthday = COALESCE(p_birthday, birthday),
            group_id = COALESCE(v_group_id, group_id)
        WHERE name = p_name AND surname = p_surname
        RETURNING id INTO v_contact_id;
    ELSE
        INSERT INTO contacts(name, surname, email, birthday, group_id)
        VALUES (p_name, p_surname, p_email, p_birthday, v_group_id)
        RETURNING id INTO v_contact_id;
    END IF;

    IF p_phone IS NOT NULL AND NULLIF(TRIM(p_phone), '') IS NOT NULL THEN
        INSERT INTO phones(contact_id, phone, type)
        VALUES (v_contact_id, TRIM(p_phone), v_phone_type)
        ON CONFLICT (contact_id, phone)
        DO UPDATE SET type = EXCLUDED.type;
    END IF;
END;
$$;


-- =========================================
-- PROCEDURE 1B: Backward-compatible alias
-- =========================================
CREATE OR REPLACE PROCEDURE upsert_user(
    p_name VARCHAR,
    p_surname VARCHAR,
    p_phone VARCHAR
)
LANGUAGE plpgsql
AS $$
BEGIN
    CALL upsert_contact(p_name, p_surname, p_phone, 'mobile', NULL, NULL, NULL);
END;
$$;


-- =========================================
-- PROCEDURE 2: Add a new phone to a contact
-- =========================================
CREATE OR REPLACE PROCEDURE add_phone(
    p_contact_name VARCHAR,
    p_phone VARCHAR,
    p_type VARCHAR
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_contact_id INTEGER;
    v_phone_type VARCHAR(10);
BEGIN
    v_phone_type := LOWER(COALESCE(NULLIF(TRIM(p_type), ''), 'mobile'));

    IF v_phone_type NOT IN ('home', 'work', 'mobile') THEN
        RAISE EXCEPTION 'Invalid phone type: %', p_type;
    END IF;

    SELECT id INTO v_contact_id
    FROM contacts
    WHERE name ILIKE p_contact_name
       OR (name || ' ' || surname) ILIKE p_contact_name
    ORDER BY id
    LIMIT 1;

    IF v_contact_id IS NULL THEN
        RAISE EXCEPTION 'Contact not found: %', p_contact_name;
    END IF;

    INSERT INTO phones(contact_id, phone, type)
    VALUES (v_contact_id, TRIM(p_phone), v_phone_type)
    ON CONFLICT (contact_id, phone)
    DO UPDATE SET type = EXCLUDED.type;
END;
$$;


-- =========================================
-- PROCEDURE 3: Move contact to a different group
-- =========================================
CREATE OR REPLACE PROCEDURE move_to_group(
    p_contact_name VARCHAR,
    p_group_name VARCHAR
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_contact_id INTEGER;
    v_group_id INTEGER;
    v_group_name VARCHAR(50);
BEGIN
    v_group_name := COALESCE(NULLIF(TRIM(p_group_name), ''), 'Other');

    INSERT INTO groups(name)
    VALUES (v_group_name)
    ON CONFLICT (name) DO NOTHING;

    SELECT id INTO v_group_id
    FROM groups
    WHERE name = v_group_name;

    SELECT id INTO v_contact_id
    FROM contacts
    WHERE name ILIKE p_contact_name
       OR (name || ' ' || surname) ILIKE p_contact_name
    ORDER BY id
    LIMIT 1;

    IF v_contact_id IS NULL THEN
        RAISE EXCEPTION 'Contact not found: %', p_contact_name;
    END IF;

    UPDATE contacts
    SET group_id = v_group_id
    WHERE id = v_contact_id;
END;
$$;


-- =========================================
-- PROCEDURE 4: Delete by name/surname or phone
-- =========================================
CREATE OR REPLACE PROCEDURE delete_contact_by_value(
    p_value VARCHAR
)
LANGUAGE plpgsql
AS $$
BEGIN
    DELETE FROM contacts c
    WHERE c.name ILIKE p_value
       OR c.surname ILIKE p_value
       OR (c.name || ' ' || c.surname) ILIKE p_value
       OR EXISTS (
           SELECT 1
           FROM phones p
           WHERE p.contact_id = c.id
             AND p.phone ILIKE p_value
       );
END;
$$;


-- =========================================
-- PROCEDURE 4B: Backward-compatible alias
-- =========================================
CREATE OR REPLACE PROCEDURE delete_user_by_value(
    p_value VARCHAR
)
LANGUAGE plpgsql
AS $$
BEGIN
    CALL delete_contact_by_value(p_value);
END;
$$;


-- =========================================
-- PROCEDURE 5: Bulk insert contacts with validation
-- =========================================
CREATE OR REPLACE PROCEDURE insert_many_users(
    p_names TEXT[],
    p_surnames TEXT[],
    p_phones TEXT[],
    p_emails TEXT[] DEFAULT NULL,
    p_birthdays TEXT[] DEFAULT NULL,
    p_groups TEXT[] DEFAULT NULL,
    p_phone_types TEXT[] DEFAULT NULL
)
LANGUAGE plpgsql
AS $$
DECLARE
    i INT;
    v_email TEXT;
    v_birthday DATE;
    v_group TEXT;
    v_phone_type TEXT;
BEGIN
    IF array_length(p_names, 1) IS DISTINCT FROM array_length(p_surnames, 1)
       OR array_length(p_names, 1) IS DISTINCT FROM array_length(p_phones, 1) THEN
        RAISE EXCEPTION 'Names, surnames, and phones arrays must have the same length';
    END IF;

    CREATE TEMP TABLE IF NOT EXISTS invalid_users (
        name TEXT,
        surname TEXT,
        phone TEXT
    ) ON COMMIT DROP;

    DELETE FROM invalid_users;

    FOR i IN 1..array_length(p_names, 1) LOOP
        v_email := CASE WHEN p_emails IS NOT NULL AND array_length(p_emails, 1) >= i THEN p_emails[i] ELSE NULL END;
        v_group := CASE WHEN p_groups IS NOT NULL AND array_length(p_groups, 1) >= i THEN p_groups[i] ELSE NULL END;
        v_phone_type := CASE WHEN p_phone_types IS NOT NULL AND array_length(p_phone_types, 1) >= i THEN p_phone_types[i] ELSE 'mobile' END;

        IF p_birthdays IS NOT NULL AND array_length(p_birthdays, 1) >= i AND NULLIF(TRIM(p_birthdays[i]), '') IS NOT NULL THEN
            v_birthday := p_birthdays[i]::DATE;
        ELSE
            v_birthday := NULL;
        END IF;

        IF p_phones[i] ~ '^[0-9+() -]{3,20}$' THEN
            CALL upsert_contact(
                p_names[i],
                p_surnames[i],
                p_phones[i],
                v_phone_type,
                v_email,
                v_birthday,
                v_group
            );
        ELSE
            INSERT INTO invalid_users(name, surname, phone)
            VALUES (p_names[i], p_surnames[i], p_phones[i]);
        END IF;
    END LOOP;
END;
$$;