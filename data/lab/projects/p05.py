from core import sql_project
TITLE = 'Ügyfélszolgálati felhasználókereső'
DESCRIPTION = "SQL injection; paraméterezett kontrollal."
def handle(params, method):
    return sql_project((5, TITLE, 'username', 'Bela'), params, method)
