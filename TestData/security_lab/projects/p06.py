from core import xss_project
TITLE = 'Visszatükrözött kereső'
DESCRIPTION = "XSS (reflected); biztonságos kontrollal."
def handle(params, method):
    return xss_project((6, TITLE, 'reflected'), params, method)
