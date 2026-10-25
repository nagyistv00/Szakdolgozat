from core import sql_project
TITLE = 'Webáruház termékkereső'
DESCRIPTION = "SQL injection; paraméterezett kontrollal."
def handle(params, method):
    return sql_project((4, TITLE, 'product_id', '1'), params, method)
