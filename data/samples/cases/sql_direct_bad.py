def find_account(cursor, user_text):
    return cursor.execute(f"SELECT name FROM accounts WHERE name = '{user_text}'")
