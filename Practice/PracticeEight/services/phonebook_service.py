import psycopg2
from db.connection import get_connection


# =========================================
# 1. Add or update one user (procedure)
# =========================================
def add_or_update_user(name, surname, phone):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("CALL upsert_user(%s, %s, %s)", (name, surname, phone))
        conn.commit()
        print("✅ User inserted/updated successfully!")

    except Exception as e:
        conn.rollback()
        print(f"❌ Error: {e}")

    finally:
        cursor.close()
        conn.close()


# =========================================
# 2. Search users (function)
# =========================================
def get_users(filter_value=None):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        if filter_value:
            cursor.execute("SELECT * FROM search_phonebook(%s)", (filter_value,))
        else:
            cursor.execute("SELECT * FROM phonebook ORDER BY id")

        users = cursor.fetchall()
        return users

    finally:
        cursor.close()
        conn.close()


# =========================================
# 3. Manual update (optional, Python side)
# =========================================
def update_user(old_name, old_surname, new_name=None, new_surname=None, new_phone=None):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        if new_name:
            cursor.execute(
                "UPDATE phonebook SET name=%s WHERE name=%s AND surname=%s",
                (new_name, old_name, old_surname)
            )

        if new_surname:
            cursor.execute(
                "UPDATE phonebook SET surname=%s WHERE name=%s AND surname=%s",
                (new_surname, old_name, old_surname)
            )

        if new_phone:
            cursor.execute(
                "UPDATE phonebook SET phone=%s WHERE name=%s AND surname=%s",
                (new_phone, old_name, old_surname)
            )

        conn.commit()
        print("✅ User updated successfully!")

    except Exception as e:
        conn.rollback()
        print(f"❌ Error: {e}")

    finally:
        cursor.close()
        conn.close()


# =========================================
# 4. Delete user by name/surname/phone (procedure)
# =========================================
def delete_user(value):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("CALL delete_user_by_value(%s)", (value,))
        conn.commit()
        print("✅ User deleted successfully!")

    except Exception as e:
        conn.rollback()
        print(f"❌ Error: {e}")

    finally:
        cursor.close()
        conn.close()


# =========================================
# 5. Pagination (function)
# =========================================
def get_users_paginated(limit, offset):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "SELECT * FROM get_phonebook_paginated(%s, %s)",
            (limit, offset)
        )
        users = cursor.fetchall()
        return users

    finally:
        cursor.close()
        conn.close()


# =========================================
# 6. Bulk insert users (procedure)
# =========================================
def insert_many_users(names, surnames, phones):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "CALL insert_many_users(%s, %s, %s)",
            (names, surnames, phones)
        )

        cursor.execute("SELECT * FROM invalid_users")
        invalid_data = cursor.fetchall()

        conn.commit()

        if invalid_data:
            print("⚠️ Invalid data found:")
            for row in invalid_data:
                print(row)
        else:
            print("✅ All users inserted successfully!")

    except Exception as e:
        conn.rollback()
        print(f"❌ Error: {e}")

    finally:
        cursor.close()
        conn.close()