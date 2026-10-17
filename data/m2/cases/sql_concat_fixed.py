def find_account(cursor, user_text):
    query = "SELECT name FROM accounts WHERE name = ?"
    return cursor.execute(query, (user_text,))
