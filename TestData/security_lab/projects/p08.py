from core import xss_project
TITLE = 'DOM előnézet'
DESCRIPTION = "XSS (dom); biztonságos kontrollal."
def handle(params, method):
    return xss_project((8, TITLE, 'dom'), params, method)
