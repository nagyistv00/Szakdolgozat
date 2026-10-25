from core import xss_project
TITLE = 'JavaScript üdvözlő'
DESCRIPTION = "XSS (js); biztonságos kontrollal."
def handle(params, method):
    return xss_project((9, TITLE, 'js'), params, method)
