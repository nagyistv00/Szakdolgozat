from core import sql_project
TITLE = 'HR alkalmazotti adatlap'
DESCRIPTION = "SQL injection; paraméterezett kontrollal."
def handle(params, method):
    return sql_project((3, TITLE, 'id', '1'), params, method)
