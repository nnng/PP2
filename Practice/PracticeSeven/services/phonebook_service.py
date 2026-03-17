from db.connection import get_connection

# add user 
import psycopg2
from db.connection import get_connection


def add_user(username, phone):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "INSERT INTO phonebook (username, phone) VALUES (%s, %s)",
            (username, phone)
        )
        conn.commit()
        print("✅ User added!")

    except psycopg2.errors.UniqueViolation:
        conn.rollback()
        print("❌ Error: This phone number already exists!")

    finally:
        cursor.close()
        conn.close()


# get users or get user by it's name
def get_users(filter_name=None):
    conn = get_connection()
    cursor = conn.cursor()

    if filter_name:
        cursor.execute(
            "SELECT * FROM phonebook WHERE username ILIKE %s",
            (f"%{filter_name}%",)
        )
    else:
        cursor.execute("SELECT * FROM phonebook")

    users = cursor.fetchall()

    cursor.close()
    conn.close()

    return users


# update info about user
def update_user(username, new_username=None, new_phone=None):
    conn = get_connection()
    cursor = conn.cursor()

    if new_username:
        cursor.execute(
            "UPDATE phonebook SET username=%s WHERE username ILIKE %s",
            (new_username, username)
        )

    if new_phone:
        cursor.execute(
            "UPDATE phonebook SET phone=%s WHERE username ILIKE %s",
            (new_phone, username)
        )

    conn.commit()
    cursor.close()
    conn.close()


# delete user
def delete_user(username=None, phone=None):
    conn = get_connection()
    cursor = conn.cursor()

    if username:
        cursor.execute(
            "DELETE FROM phonebook WHERE username ILIKE %s",
            (username,)
        )
    elif phone:
        cursor.execute(
            "DELETE FROM phonebook WHERE phone=%s",
            (phone,)
        )

    conn.commit()
    cursor.close()
    conn.close()

  
