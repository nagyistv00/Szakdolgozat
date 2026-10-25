from core import xss_project
TITLE = 'Vendégkönyv'
DESCRIPTION = "XSS (stored); biztonságos kontrollal."
def handle(params, method):
    return xss_project((7, TITLE, 'stored'), params, method)
