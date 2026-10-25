from core import xss_project
TITLE = 'Dokumentum előnézet'
DESCRIPTION = "XSS (write); biztonságos kontrollal."
def handle(params, method):
    return xss_project((10, TITLE, 'write'), params, method)
