-- =========================================
-- PROCEDURE 1: Insert or update one contact
-- =========================================
CREATE OR REPLACE PROCEDURE upsert_user(
    p_name VARCHAR,
    p_surname VARCHAR,
    p_phone VARCHAR
)
LANGUAGE plpgsql
AS $$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM phonebook
        WHERE name = p_name AND surname = p_surname 
    ) THEN
        UPDATE phonebook
        SET phone = p_phone
        WHERE name = p_name AND surname = p_surname;
    ELSE
        INSERT INTO phonebook(name, surname, phone)
        VALUES (p_name, p_surname, p_phone);
    END IF;
END;
$$;


-- =========================================
-- PROCEDURE 2: Delete by name/surname or phone
-- =========================================
CREATE OR REPLACE PROCEDURE delete_user_by_value(
    p_value VARCHAR
)
LANGUAGE plpgsql
AS $$
BEGIN
    DELETE FROM phonebook
    WHERE phone = p_value
       OR name = p_value
       OR surname = p_value;
END;
$$;


-- =========================================
-- PROCEDURE 3: Bulk insert users with validation
-- =========================================
CREATE OR REPLACE PROCEDURE insert_many_users(
    p_names TEXT[],
    p_surnames TEXT[],
    p_phones TEXT[]
)
LANGUAGE plpgsql
AS $$
DECLARE
    i INT;
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
        IF p_phones[i] ~ '^[0-9]{10,15}$' THEN
            IF EXISTS (
                SELECT 1
                FROM phonebook
                WHERE name = p_names[i] AND surname = p_surnames[i]
            ) THEN
                UPDATE phonebook
                SET phone = p_phones[i]
                WHERE name = p_names[i] AND surname = p_surnames[i];
            ELSE
                BEGIN
                    INSERT INTO phonebook(name, surname, phone)
                    VALUES (p_names[i], p_surnames[i], p_phones[i]);
                EXCEPTION
                    WHEN unique_violation THEN
                        INSERT INTO invalid_users(name, surname, phone)
                        VALUES (p_names[i], p_surnames[i], p_phones[i]);
                END;
            END IF;
        ELSE
            INSERT INTO invalid_users(name, surname, phone)
            VALUES (p_names[i], p_surnames[i], p_phones[i]);
        END IF;
    END LOOP;
END;
$$;