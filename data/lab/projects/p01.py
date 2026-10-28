from core import sql_project
TITLE = 'Felhasználói névjegyzék'
DESCRIPTION = "SQL injection; paraméterezett kontrollal."
def handle(params, method):
    return sql_project((1, TITLE, 'username', 'Anna'), params, method)
