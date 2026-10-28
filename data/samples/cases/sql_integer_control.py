def find_account(cursor, user_text):
    account_id = int(user_text)
    return cursor.execute(f"SELECT name FROM accounts WHERE id = {account_id}")
