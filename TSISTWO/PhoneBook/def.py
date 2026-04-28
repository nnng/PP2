from db.connection import get_connection

conn = get_connection()
cursor = get_connection.cursor()

cursor.execute("CALL delete_user_by_value(%s)" , ("Timur"))

cursor.commit()
cursor.exit()
conn.exit()