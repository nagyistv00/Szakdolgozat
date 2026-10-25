from core import sql_project
TITLE = 'Ügyfél CRM'
DESCRIPTION = "SQL injection; paraméterezett kontrollal."
def handle(params, method):
    return sql_project((2, TITLE, 'email', 'user1@example.test'), params, method)
