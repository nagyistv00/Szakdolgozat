def find_account(cursor, user_text):
    query = "SELECT name FROM accounts WHERE name = '" + user_text + "'"
    return cursor.execute(query)
