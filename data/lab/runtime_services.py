"""Az app.py életciklusához kötött SMTP és tartós háttérfeladat-ütemező."""
import json
import threading
import time
from core import query

class Services:
    def __init__(self,host,smtp_port):
        self.host=host;self.port=smtp_port;self.smtp=None
        self.stop_event=threading.Event();self.worker=None
    def start(self):
        query('CREATE TABLE IF NOT EXISTS runtime_metrics (id INTEGER PRIMARY KEY, captured_at TEXT, snapshot TEXT)')
        if self.port:
            from smtp_local import start_smtp
            self.smtp=start_smtp(self.host,self.port)
        self.worker=threading.Thread(target=self.run,name='lab-metrics',daemon=True)
        self.worker.start()
    def run(self):
        while not self.stop_event.is_set():
            snapshot={key:query('SELECT COUNT(*) AS n FROM '+table)[0]['n'] for key,table in [('records','items'),('mail','mail'),('purchases','purchases')]}
            query('INSERT INTO runtime_metrics(captured_at,snapshot) VALUES (?,?)',(time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),json.dumps(snapshot)))
            query('DELETE FROM runtime_metrics WHERE id NOT IN (SELECT id FROM runtime_metrics ORDER BY id DESC LIMIT 120)')
            self.stop_event.wait(30)
    def stop(self):
        self.stop_event.set()
        if self.worker: self.worker.join(timeout=2)
        if self.smtp: self.smtp.shutdown(); self.smtp.server_close()
